#!/usr/bin/env python
# Copyright (c) 2014, Team 3710 and Team 256
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#       ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#       ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#       The views and conclusions contained in the software and documentation are those
#       of the authors and should not be interpreted as representing official policies,
#       either expressed or implied, of the FreeBSD Project.

# ~~~~~~~~~~~~~~~~~~~~~~~
# ~~~ Visual Joystick ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~
#
# This Python script uses your laptop's webcam and OpenCV to get a 2-axis, 4-button 
# joystick during autonomous mode. The values are sent to the cRIO and what you do
# with it is up to you!
#
# When you start the program you will need to enter your team number so we can find
# the IP of your cRIO. You will then have to select two vision targets of distinct colours,
# I used red and blue stress balls. It is important to pick something which will be
# a distinct colour from the background. To calibrate your two vision targets use the two
# calibration windows that should pop up. Use the minH and maxH sliders to select a range
# of hue values to segment your target from the background. One of your targets will then
# act as a two axis joystick, and the other will activate the four buttons at the bottom.
# The values of your configuration are saved to the file 'parameters.yaml' so that they should
# persist between runs. Note that hue is strongly effected by the lighting conditions of your
# room, so you may need to adjust the values every time you change rooms, and *ESPECIALLY*
# under the arena lights at the competition venue.
#
# To quit press 'esc' in the webcam window.
#
# Enjoy!
import socket, time, copy
import numpy as np
import cv2
import Tkinter
from Tkinter import *
import yaml


HOST, PORT = "10.37.10.2", 1180

# Dimensions of the webcam image (it will be resized to this size)
WEBCAM_WIDTH_PX = 640
WEBCAM_HEIGHT_PX = 480

# This is the rate at which we will send updates to the cRIO.
UPDATE_RATE_HZ = 40.0
PERIOD = (1.0 / UPDATE_RATE_HZ) * 1000.0

paramsFile = 'params.yaml'

# pixel centres for the 4 buttons
btn1Ctr = (77, 415)
btn2Ctr = (217, 415)
btn3Ctr = (415, 415)
btn4Ctr = (558, 415)
btnRadiusSq = 40*40

def get_time_millis():
    ''' Get the current time in milliseconds. '''
    return int(round(time.time() * 1000))

def set_cRIO_IP( teamNo ) :
	global HOST
	
	if( len(teamNo) <= 2) :
		HOST = "10.0."+str(teamNo)+".2"
	else :
		HOST = "10."+str( teamNo[:2] )+"."+teamNo[2:]+".2"
		
	
# static parameters for object detection, throw away anything too saturated, or too dark, or too small
minS = 40
maxS = 255
minV = 40
maxV = 255
minSize = 0.001
def detect( img, minH, maxH, noiseFilterSize, windowName ) :
	'''This function detects an object given the min and max hues and the noise filter size. This code is general and is re-used for both objects.'''
	# convert image to HSV space and threshold it
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	# threshold the color
	mask = cv2.inRange( hsv, np.array( [minH, minS, minV], np.uint8 ), np.array( [maxH, maxS, maxV], np.uint8 ) )
	
	# noise filter
	#cv.Smooth( mask, mask, cv.CV_MEDIAN, 2*noiseFilterSize+1);
	mask = cv2.medianBlur( mask,2*noiseFilterSize+1);
	
	cv2.imshow(windowName, mask )
	
	# compute the centre of mass
	# the basic idea is to the (x,y) coordinate by its binar {0,1} detected mask, then average them
	# the numpy linear algebra (aka vectorization) makes this MUCH faster, but also harder to read
	h,w = mask.shape
	ys = np.array( range( h ) )
	ys = np.tile( np.array( range(h) ), ( w, 1) ).transpose()
	
	xs = np.array( range( w ) )
	xs = np.tile( np.array( range(w) ), ( h, 1) )
	
	npMask = mask.astype(float) / 255
	
	sum = np.sum(npMask)
	if (sum / (w*h) < minSize) :
		return -1, -1
		
	meanX = int( np.sum( xs * npMask ) / sum )
	meanY = int( np.sum( ys * npMask ) / sum )
	
	return meanX, meanY
	
def writeParams( args ) :
	'''Save the parameters to YAML file so they persist between runs.'''
	global joystick_minH, joystick_maxH, joystick_noiseFilterSize
	global button_minH, button_maxH, button_noiseFilterSize
	global teamNo
	
	joystick_minH = cv2.getTrackbarPos("minH_joystick", "Calibrate Joystick")
	joystick_maxH = cv2.getTrackbarPos("maxH_joystick", "Calibrate Joystick")
	joystick_noiseFilterSize = cv2.getTrackbarPos("size of noise filter joystick", "Calibrate Joystick")
	
	button_minH = cv2.getTrackbarPos( "minH_button", "Calibrate Button")
	button_maxH = cv2.getTrackbarPos( "maxH_button", "Calibrate Button")
	button_noiseFilterSize = cv2.getTrackbarPos( "size of noise filter button", "Calibrate Button")
	
	params = {}
	params["joystick_minH"] = joystick_minH
	params["joystick_maxH"] = joystick_maxH
	params["joystick_noiseFilterSize"] = joystick_noiseFilterSize
	params["button_minH"] = button_minH
	params["button_maxH"] = button_maxH
	params["button_noiseFilterSize"] = button_noiseFilterSize
	params['teamNo'] = teamNo
	
	# convert this string to YAML formated string
	YAMLstr = yaml.dump( params )
	
	# save it to a file
	file = open(paramsFile, 'w')
	file.write(YAMLstr)
	file.close()
	
def readParams() :
	'''Read the params from a previous run from a YAML file.'''
	global joystick_minH, joystick_maxH, joystick_noiseFilterSize
	global button_minH, button_maxH, button_noiseFilterSize
	global teamNo
	
	joystick_minH = joystick_maxH = joystick_noiseFilterSize = 0
	button_minH = button_maxH = button_noiseFilterSize = 0
	teamNo = ''
	
	try :
		file = open(paramsFile, 'r')
	except IOError:
		# file not there, use the default parameters
		return
		
	input = file.read()
	file.close()
	
	# convert the raw text into a dictionary
	params = yaml.load( input )
	
	# extract the individual variables
	try :
		joystick_minH = params["joystick_minH"]
		joystick_maxH = params["joystick_maxH"]
		joystick_noiseFilterSize = params["joystick_noiseFilterSize"]
		button_minH = params["button_minH"]
		button_maxH = params["button_maxH"]
		button_noiseFilterSize = params["button_noiseFilterSize"]
		teamNo = params['teamNo']
	except KeyError as e :
		# the file was corrupt, go with the default values
		print("File Corrupt")
		return

joyColour = (0, 255, 0)
btnColour = (255, 0, 0)
alpha = 0.6 # for the smoothing to reduce jitter
def run( ) :
	'''The main function for the OpenCV tracker.'''
	
	global joystick_minH, joystick_maxH, joystick_noiseFilterSize
	global button_minH, button_maxH, button_noiseFilterSize
	global teamNo
	global top, teamNoEntry, WINDOW_NAME
	
	readParams()
	
	# deal with the GUI stuff from the last window
	teamNo = teamNoEntry.get()
	if( len(teamNo) == 0 or len(teamNo) > 4) : teamNo = '0000'
	set_cRIO_IP( teamNo )
	top.destroy()
		
	# create the trackbars (aka sliders)
	cv2.namedWindow("Calibrate Joystick", 1)
	cv2.createTrackbar( "minH_joystick", "Calibrate Joystick", joystick_minH, 180, writeParams)
	cv2.createTrackbar( "maxH_joystick", "Calibrate Joystick", joystick_maxH, 180, writeParams)
	cv2.createTrackbar( "size of noise filter joystick", "Calibrate Joystick", joystick_noiseFilterSize, 25, writeParams)
    
	cv2.namedWindow("Calibrate Button", 1)
	cv2.createTrackbar( "minH_button", "Calibrate Button", button_minH, 180, writeParams)
	cv2.createTrackbar( "maxH_button", "Calibrate Button", button_maxH, 180, writeParams)
	cv2.createTrackbar( "size of noise filter button", "Calibrate Button", button_noiseFilterSize, 25, writeParams)
	cv2.waitKey(5);
	
	WINDOW_NAME = "Visual Joystick for Team "+teamNo
	cv2.namedWindow(WINDOW_NAME, 1)
	
	writeParams( 0 )

	# Open the webcam (should be the only video capture device present).
	capture = cv2.VideoCapture(0)

	# Keep track of time so that we can provide the cRIO with a relatively constant
	# flow of data.
	last_t = get_time_millis()

	# Are we connected to the server on the robot?
	connected = False
	s = None

	oldJoyX = oldJoyY = oldBtnX = oldBtnY  = 0
	while 1:
		# Grab a new frame.
		_, img = capture.read()
		height, width, _ = img.shape
		
		# Mirror it and shrink it to the same size as the overlay
		img = cv2.flip(cv2.resize(img, (WEBCAM_WIDTH_PX, WEBCAM_HEIGHT_PX)), 1)

		# detect the joystick and button objects in the image
		joyX, joyY = detect( img, joystick_minH, joystick_maxH, joystick_noiseFilterSize, "Calibrate Joystick")
		btnX, btnY = detect( img, button_minH, button_maxH, button_noiseFilterSize, "Calibrate Button")
		
		# did it detect a joystick object?
		if (joyX != -1 and joyY != -1) :
			# do some smoothing to remove jitter
			joyX = int( alpha*joyX + (1-alpha)*oldJoyX )
			joyY = int( alpha*joyY + (1-alpha)*oldJoyY )
			oldJoyX = joyX
			oldJoyY = joyY
						
			# draw it
			cv2.circle( img, (joyX, joyY), 15, joyColour, thickness=-1 )
		
		# did it detect a button object?
		overlayFile = 'axes.png'
		btnPressed = 0
		if (btnX != -1 and btnY != -1) :
			# do some smoothing to remove jitter
			btnX = int( alpha*btnX + (1-alpha)*oldBtnX )
			btnY = int( alpha*btnY + (1-alpha)*oldBtnY )
			oldBtnX = btnX
			oldBtnY = btnY
						
			# draw it
			cv2.circle( img, (btnX, btnY), 15, btnColour, thickness=-1 )
			
			# is it within any of the button circles?
			distSqBtn1 = (btnX - btn1Ctr[0])*(btnX - btn1Ctr[0]) + (btnY - btn1Ctr[1])*(btnY - btn1Ctr[1])
			distSqBtn2 = (btnX - btn2Ctr[0])*(btnX - btn2Ctr[0]) + (btnY - btn2Ctr[1])*(btnY - btn2Ctr[1])
			distSqBtn3 = (btnX - btn3Ctr[0])*(btnX - btn3Ctr[0]) + (btnY - btn3Ctr[1])*(btnY - btn3Ctr[1])
			distSqBtn4 = (btnX - btn4Ctr[0])*(btnX - btn4Ctr[0]) + (btnY - btn4Ctr[1])*(btnY - btn4Ctr[1])
			
			if( distSqBtn1 < btnRadiusSq ) :
				overlayFile = 'axesB1.png'
				btnPressed = 1
			elif( distSqBtn2 < btnRadiusSq ) :
				overlayFile = 'axesB2.png'
				btnPressed = 2
			elif( distSqBtn3 < btnRadiusSq ) :
				overlayFile = 'axesB3.png'
				btnPressed = 3
			elif( distSqBtn4 < btnRadiusSq ) :
				overlayFile = 'axesB4.png'
				btnPressed = 4
			else :
				overlayFile = 'axes.png'
				btnPressed = 0
			
		# overlay axes and some buttons
		overlay = cv2.imread(overlayFile)
		
		# detect which pixels in the overlay have something in them
		# and make a binary mask out of it
		overlayMask = cv2.cvtColor( overlay, cv2.COLOR_BGR2GRAY )
		res, overlayMask = cv2.threshold( overlayMask, 10, 1, cv2.THRESH_BINARY_INV)
		
		# expand the mask from 1-channel to 3-channel
		h,w = overlayMask.shape
		overlayMask = np.repeat( overlayMask, 3).reshape( (h,w,3) )
		
		# mask out the pixels that you want to overlay
		img *= overlayMask
		img += overlay
		
		# Show the image.
		cv2.imshow(WINDOW_NAME, img)

		cur_time = get_time_millis()
		if (last_t + PERIOD <= cur_time):
			# Try to connect to the robot on open or disconnect
			if not connected:
				try:
					# Open a socket with the cRIO so that we can send the state of the hot goal.
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

					# This is a pretty aggressive timeout...we want to reconnect automatically
					# if we are disconnected.
					s.settimeout(.1)
					s.connect((HOST, PORT))
				except:
					print "failed to reconnect"
					last_t = cur_time + 1000
			try:
				# data format:
				# "Xaxis,Yaxis,btn1,btn2,btn3,btn4"
				# so a typical message will look like:
				# "0.625,-0.591666666667,0,0,0,0"
				
				# the target-not-found condition:
				if( joyX < 0 or joyY < 0) :
					msg = "-100,-100"
				else :
					Xaxis = 2*( float(joyX) / width) - 1
					Yaxis = 1 - 2*( float(joyY) / height)
					msg = str(Xaxis)+","+str(Yaxis)
					
				if( btnPressed == 0 ) :
					msg = msg+",0,0,0,0"
				elif( btnPressed == 1 ) :
					msg = msg+",1,0,0,0"
				elif( btnPressed == 2 ) :
					msg = msg+",0,1,0,0"
				elif( btnPressed == 3 ) :
					msg = msg+",0,0,1,0"
				elif( btnPressed == 4 ) :
					msg = msg+",0,0,0,1"
					
				print( msg )
				s.send(msg)
				last_t = cur_time
				connected = True
			except:
				#print "Could not send data to robot"
				connected = False

		# Capture a keypress.
		key = cv2.waitKey(10) & 255

		# Escape key.
		if key == 27:
			break

	try:
		s.close()
	except :
		pass

def main():
	global top, teamNoEntry
	global teamNo
	
	readParams()
	
	top = Tk()
    
	top.title("FRC Visual Joystick")
	top.resizable(0, 0)
	top.geometry(("%dx%d")%(250,100))

	instructLbl = Label(top, text="Team No.")
	instructLbl.grid(row=0, sticky=N+E+W+S)

	teamNoEntry = Entry(top, width=6)
	teamNoEntry.insert(0, teamNo)
	teamNoEntry.grid(row=1, sticky=N+E+W+S)

	updateBtn = Button(top, text="Go!", command=run)
	updateBtn.grid(row=2, sticky=N+S)

	top.mainloop()
    

if __name__ == '__main__':
    main()

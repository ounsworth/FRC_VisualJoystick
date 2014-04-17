FRC Visual Joystick
==================

A 2-axis, 4-button "joystick" using the Driver Station's webcam for the FIRST Robotics Competition.
       
This Python script uses your laptop's webcam and OpenCV to get a 2-axis, 4-button 
joystick during autonomous mode. The values are sent to the cRIO and what you do
with it is up to you!

When you start the program you will need to enter your team number so we can find
the IP of your cRIO. You will then have to select two vision targets of distinct colours,
I used red and blue stress balls. It is important to pick something which will be
a distinct colour from the background. To calibrate your two vision targets use the two
calibration windows that should pop up. Use the minH and maxH sliders to select a range
of hue values to segment your target from the background. One of your targets will then
act as a two axis joystick, and the other will activate the four buttons at the bottom.
The values of your configuration are saved to the file 'parameters.yaml' so that they should
persist between runs. Note that hue is strongly effected by the lighting conditions of your
room, so you may need to adjust the values every time you change rooms, and *ESPECIALLY*
under the arena lights at the competition venue.
To quit press 'esc' in the webcam window.

Enjoy!


# Running it

I have provided two ways of running it:
 
 1. I have bundled this into a standalone exe. Grab the VisualJoystick_win.zip, extract it and inside run visualjoystick.exe. I bundled this with cx_freeze on my Windows 7, AMD x86 machine. I make no claims that this will work on all machines since I'm a linux guy and Windows development seems like ~Black~Magic~.
 2. If the bundled exe doesn't work, or you want to modify the source then you'll need to install the following stuff:
  1. Python 2.7
   https://www.python.org/download/
  2. Numpy
   http://sourceforge.net/projects/numpy/files/
  3. OpenCV - this one is a bit tricky, once you've run the installer you need to copy this file:
   opencv\build\python\2.7\x86\cv2.pyd
  to
   C:\Python27\Lib\site-packages
	http://sourceforge.net/projects/opencvlibrary/files/opencv-win/
  4. YAML
   http://pyyaml.org/wiki/PyYAML
 
       
   
# GPLv3 license stuff

 
Copyright (c) 2014, Team 3710 and Team 256 All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

      THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
      ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
      WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
      DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
      ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
      (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
      LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
      ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
      (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
      SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

      The views and conclusions contained in the software and documentation are those
      of the authors and should not be interpreted as representing official policies,
      either expressed or implied, of the FreeBSD Project.

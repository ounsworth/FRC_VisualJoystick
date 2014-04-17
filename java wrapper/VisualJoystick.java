package ???;

/**
 * @author Mike Ounsworth
 * Team 3710, The Cyber Falcons
 * 
 * With code from
 * Tom Bottiglieri
 * Team 254, The Cheesy Poofs
 * 
 * This code comes with a GPLv3 license, feel free to use, modify, distrubute, etc to your heart's content
 * provided that credit is given to the original authors.
 */

import edu.wpi.first.wpilibj.Timer;
import java.io.IOException;
import java.io.InputStream;
import java.util.Vector;
import java.util.concurrent.Semaphore;
import javax.microedition.io.Connector;
import javax.microedition.io.ServerSocketConnection;
import javax.microedition.io.SocketConnection;

class VisualJoystick implements Runnable {
	
	/** This file has all the public methods at the top, then the implementation details below. **/


	/** Joystick Variables **/
	private float x_axis, y_axis;
	private boolean btn1, btn2, btn3, btn4;


	/** 
	 * The x_axia dn y_axis are both scaled to [-1,1] just like any other joystick.
	 * 
	 * Note that if no object is detected, or there is a communication error
	 * the x_axis and y_axis will both be -100,
	 * so it is advisable to check 
	 * if (joy.getX() < -1)
	 *     // ignore
	 **/
	public float getX() {
		float var = x_axis;
		return var;
	}

	public float getY() {
		float var = y_axis;
		return var;
	}

	public boolean getButton1(){
		return btn1;
	}

	public boolean getButton2(){
		return btn2;
	}
	
	public boolean getButton3(){
		return btn3;
	}
	
	public boolean getButton4(){
		return btn4;
	}

	public void start() {
	  serverThread.start();
	}

	public void stop() {
	  listening_  = false;
	}
	
	public boolean hasClientConnection() {
		return lastHeartbeatTime_ > 0 && (Timer.getFPGATimestamp() - lastHeartbeatTime_) < 3.0; 
	}

	public void setPort(int port) {
		listenPort_ = port;
	}
	
	
	/*******************************************************************************
	 ** From here on is network / socket stuff, only read on if you're interested **
	 *******************************************************************************/
	
	/** Socket Variables **/
	private static VisualJoystick instance_;
	Thread serverThread = new Thread(this);
	private int listenPort_;
	private Vector connections_;
	double lastHeartbeatTime_ = -1;
	private boolean listening_ = true;
	
	/** just to make it thread-safe since the socket server is running multiple threads **/
	private Semaphore mutex = new Semaphore(1);
	
	public static VisualJoystick getInstance() {
      if (instance_ == null) {
          instance_ = new VisualJoystick();
      }
      return instance_;
	}

	private VisualJoystick() {
		this(1180);
	}

	private VisualJoystick(int port) {
		listenPort_ = port;
		connections_ = new Vector();
	}
	
	// This class handles incoming TCP connections
	private class VisionServerConnectionHandler implements Runnable {

		SocketConnection connection;

		public VisionServerConnectionHandler(SocketConnection c) {
		  connection = c;
		}
		
		private static boolean stringToBool(String s) {
		  if (s.equals("1"))
			return true;
		  else
			return false;
		}

		public void run() {
		  try {
			InputStream is = connection.openInputStream();

			int ch = 0;
			byte[] b = new byte[1024];
			double timeout = 10.0;
			double lastHeartbeat = Timer.getFPGATimestamp();
			VisualJoystick.this.lastHeartbeatTime_ = lastHeartbeat;
			while (Timer.getFPGATimestamp() < lastHeartbeat + timeout) {
			  boolean gotData = false;
			  while (is.available() > 0) {
				gotData = true;
				int read = is.read(b);
				String rawData = String(b, 0, read)
				String[] tokens = rawData.split(",");
				
				// let's make this thread-safe
				mutex.acquire();
				try {
					VisualJoystick.this.x_axis = Double.parseDouble(tokens[0]);
					VisualJoystick.this.y_axis = Double.parseDouble(tokens[1]);
					VisualJoystick.this.btn1 = stringToBool(tokens[2]);
					VisualJoystick.this.btn2 = stringToBool(tokens[3]);
					VisualJoystick.this.btn3 = stringToBool(tokens[4]);
					VisualJoystick.this.btn4 = stringToBool(tokens[5]);
				catch( Exception e ) {
					// something went wrong, return an error value
					VisualJoystick.this.x_axis = -100;
					VisualJoystick.this.y_axis = -100;
					VisualJoystick.this.btn1 = false;
					VisualJoystick.this.btn2 = false;
					VisualJoystick.this.btn3 = false;
					VisualJoystick.this.btn4 = false;
				}
				mutex.release();
				
				lastHeartbeat = Timer.getFPGATimestamp();
				VisualJoystick.this.lastHeartbeatTime_ = lastHeartbeat;
			  }

			  try {
				Thread.sleep(50); // sleep a bit
			  } catch (InterruptedException ex) {
				System.out.println("Thread sleep failed.");
			  }
			}
			is.close();
			connection.close();

		  } catch (IOException e) {
		  }
		}
	}

	// run() to implement Runnable
	// This method listens for incoming connections and spawns new
	// VisionServerConnectionHandlers to handle them
	public void run() {
		ServerSocketConnection s = null;
		try {
		  s = (ServerSocketConnection) Connector.open("serversocket://:" + listenPort_);
		  while (listening_) {
			SocketConnection connection = (SocketConnection) s.acceptAndOpen();
			Thread t = new Thread(new VisualJoystick.VisionServerConnectionHandler(connection));
			t.start();
			connections_.addElement(connection);
			try {
			  Thread.sleep(100);
			} catch (InterruptedException ex) {
			  System.out.println("Thread sleep failed.");
			}
		  }
		} catch (IOException e) {
		  System.out.println("Socket failure.");
		  e.printStackTrace();
		}
	}
}

/*----------------------------------------------------------------------------*/
/* Copyright (c) FIRST 2008. All Rights Reserved.                             */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package ????;


import VisualJoystick;
import edu.wpi.first.wpilibj.IterativeRobot;

/**
 * @author Mike Ounsworth
 * Team 3710, The Cyber Falcons
 * 
 * with code from
 * Tom Bottiglieri
 * Team 254, The Cheesy Poofs
 */
public class VisualJoystickRobot extends IterativeRobot {

    VisualJoystick visjoy = VisualJoystick.getInstance();
    
    public void robotInit() {
        server.start();
    }

    public void autonomousInit() {
		
    }
    
    public void disabledInit() {
		
    }
    

    public void autonomousPeriodic() {
		
		// Unlike regular joysticks, the VisualJoystick socket server is not synched to the iterative robot loop,
		// so the values may change at any point. Therefore I recommend that you 
		// ask for the values once and then make decisions based on your local variables.
		float x_axis = visjoy.getX();
		float y_axis = visjoy.getY();
		// check for errors
		if( x_axis > -1 && y_axis > -1) {
			// drive!
		}
		
		if( visjoy.getButton1() ) {
			// shoot!
		}
	}
}

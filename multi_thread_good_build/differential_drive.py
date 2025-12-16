from stepper_motor import StepperMotor
import math
import time
class DifferentialDrive:
    def __init__(self, left, right):
        """
        Initialize the navigation system with two stepper motors.

        :param left: Instance of StepperMotor class for the left motor.
        :param right: Instance of StepperMotor class for the right motor.

        """

        self.left = left
        self.right = right

        self.stop()
    
    def set_speed(self,left_pwm,right_pwm, left_speed, right_speed, mode):
        self.left.set_speed(left_pwm, left_speed, mode)
        self.right.set_speed(right_pwm, right_speed, mode)
        
        
    def forward(self, mode):
        """Perform ONE forward microstep."""
        for l_step, r_step in zip(self.left.step_sequence, self.right.step_sequence):
            self.left.set_step(l_step)
            self.right.set_step(r_step)

    def backward(self, mode):
        """Perform ONE backward microstep."""
        for l_step, r_step in zip(reversed(self.left.step_sequence), reversed(self.right.step_sequence)):
            self.left.set_step(l_step)
            self.right.set_step(r_step)
            
                        
    def stop(self):
        """
        Stop both stepper motors. 
        
        """
        self.left.stop()
        self.right.stop()
        
        
        
        
        
        
        
        
        
    def move_one_stepper(self, steps, stepper, direction="forward", mode="HALF"):
        """
        Move either left or right stepper a certain number of steps.

        :param steps: number of steps
        :param stepper: "left" or "right"
        :param direction: "forward" or "backward"
        :param mode: "FULL" or "HALF"
        """

        if stepper == "left":
            seq = self.left.step_sequence
            motor = self.left
        elif stepper == "right":
            seq = self.right.step_sequence
            motor = self.right
        else:
            raise ValueError("Must be 'left' or 'right'")

        # Reverse sequence for backward
        if direction == "backward":
            seq = list(reversed(seq))

        for _ in range(steps):
            for step in seq:
                motor.set_step(step)

                # match your forward() delay
                if mode == "HALF":
                    time.sleep(0.001)
                else:
                    time.sleep(0.0005)

        
    def cm_to_steps(self, distance_cm):
        """
        Convert a distance in centimeters to the corresponding number of motor steps.
        :param distance_cm (INT): Distance to move in centimeters.
        :return: Number of steps corresponding to the given distance.
        """

        # --> wheel_circumference_cm: 

        wheel_diameter_cm = 8.7  # Example diameter in cm
        circumference_cm = 2 * math.pi * (wheel_diameter_cm / 2)

        # --> steps_per_revolution:
        step_sequences_per_revolution = 50  # Example value, adjust as needed

         # 1) Calculate the distance per step
        distance_per_step_cm = circumference_cm / step_sequences_per_revolution

        # 2) Calculate the number of steps
        steps = int(distance_cm / distance_per_step_cm)
        
       

        # Return the calculated number of steps based on the distance
        return steps
        
    def turn_degrees(self, direction, degrees):
        """
        Turns the robot a given number of degrees in a specified direction
        
        :param direction (STR): The direction we want to turn in.
        :param degrees (INT): Amount of degrees we want to turn.
        """
        circumference = math.pi * 25
        distance = circumference/(360/degrees)
        steps = self.cm_to_steps(distance)*2
        
        if direction == "right":
            self.move_one_stepper(steps, "right")
            
        elif direction == "left":
            self.move_one_stepper(steps, "left")
        else:
            raise ValueError("Must be right or left")
        self.stop()

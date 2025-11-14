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
        
    def move_one_stepper(self, steps, stepper):
        """
        Move either left or right stepper a certain amount of steps.
        
        :param steps (INT): Number of steps to turn
        :param stepper (STR): Stepper to turn
        
        """
        step_seq_len = len(self.left.step_sequence)
        if stepper == "left":
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[i])
        elif stepper == "right":
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.right.set_step(self.left.step_sequence[i])
        else:
            raise ValueError("Must be right or left")
        
    def move_one_stepper_back(self, steps, stepper):
        """
        Move either left or right stepper a certain amount of steps.
        
        :param steps (INT): Number of steps to turn
        :param stepper (STR): Stepper to turn
        
        """
        step_seq_len = len(self.left.step_sequence)
        if stepper == "left":
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[-i])
        elif stepper == "right":
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.right.set_step(self.left.step_sequence[-i])
        else:
            raise ValueError("Must be right or left")
            
        #SKAL ÆNDRES    
    def forward(self, steps):
        """Move both motors forward."""
        for _ in range(steps):
            for l_step, r_step in zip(self.left.step_sequence, self.right.step_sequence):
                self.left.set_step(l_step)
                self.right.set_step(r_step)
        self.stop()

    def backward(self, mode):
        """Perform ONE backward microstep."""
        for l_step, r_step in zip(reversed(self.left.step_sequence), reversed(self.right.step_sequence)):
            self.left.set_step(l_step)
            self.right.set_step(r_step)
            if mode == "HALF":
                time.sleep(0.001)
                        
    def stop(self):
        """
        Stop both stepper motors. 
        
        """
        self.left.stop()
        self.right.stop()
    
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
        
        #Print for debugging
        #print(f"Distance per step: {distance_per_step_cm} cm")

        # Return the calculated number of steps based on the distance
        return steps
        

    def move_distance(self, direction, distance_cm):
        """
        Move the robot forward or backward a specific distance in centimeters.

        :param distance_cm: Distance to move in centimeters.
        :param direction: Direction to move, either 'forward' or 'backward'.
        """

        steps = self.cm_to_steps(distance_cm)
        if direction == "forward":
            self.forward(steps)
        
        if direction == "backward":
            self.backward(steps)

        self.stop()

    def turn_steps(self, direction, steps_for_rotation):
        """
        Turns the robot a given number of steps in a specified direction.
        
        :param direction (STR): The direction we want to move in.
        :param steps_for_rotation (INT): Amount of steps we want to move.
        """
        
        if direction == "right":
            self.move_one_stepper(steps_for_rotation, "left")
            
        elif direction == "left":
            self.move_one_stepper(steps_for_rotation, "right")
        else:
            raise ValueError("Must be right or left")
        self.stop()
        
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
            self.move_one_stepper(steps, "left")
            
        elif direction == "left":
            self.move_one_stepper(steps, "right")
        else:
            raise ValueError("Must be right or left")
        self.stop()
        
    def turn_degrees_back(self, direction, degrees):
        """
        Turns the robot a given number of degrees in a specified direction
        
        :param direction (STR): The direction we want to turn in.
        :param degrees (INT): Amount of degrees we want to turn.
        """
        circumference = math.pi * 25
        distance = circumference/(360/degrees)
        steps = self.cm_to_steps(distance)*2
        
        if direction == "right":
            self.move_one_stepper_back(steps, "right")
            
        elif direction == "left":
            self.move_one_stepper_back(steps, "left")
        else:
            raise ValueError("Must be right or left")
        self.stop()

    def turn_in_place(self, direction, degrees):
        """
        Turns the robot around its axis in a given number of degrees
        
        :param direction (STR): The direction we want to turn in.
        :param degrees (INT): Amount of degrees we want to turn.

        """
        circumference = math.pi * 25
        distance = circumference/(360/degrees)
        steps = self.cm_to_steps(distance)
        
        if direction == "right":
            step_seq_len = len(self.left.step_sequence)
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[i])
                    self.right.set_step(self.right.step_sequence[-i])
            self.stop()
            
        elif direction == "left":
            step_seq_len = len(self.left.step_sequence)
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[-i])
                    self.right.set_step(self.right.step_sequence[i])
            self.stop()
        else:
            raise ValueError("Must be right or left")
        self.stop()
from small_stepper_motor import SmallStepperMotor
import math
import time

class SmallDifferentialDrive:
    def __init__(self, left, right):

        self.left = left
        self.right = right
        
        self.stop()
        
    def move_one_stepper(self, steps, stepper):
        """
        Move either left or right stepper a certain amount of steps.
        
        :param steps (INT): Number of steps to turn
        :param stepper (STR): Stepper to turn
        
        """
        if stepper == "left":
            step_seq_len = len(self.left.step_sequence)
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[i])
            self.stop()
        elif stepper == "right":
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.right.set_step(self.left.step_sequence[i])
            self.stop()
        else:
            raise ValueError("Must be right or left")

    def forward(self, steps):
        for step in range(steps):
            self.left.step(1)
            self.right.step(2)
        self.stop()

    def backward(self, steps):
        for step in range(steps):
            self.left.step(-1)
            self.right.step(-1)
        self.stop()
                
    def stop(self):
        """
        Stop both stepper motors. 
        
        """
        self.left.stop()
        self.right.stop()

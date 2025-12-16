from machine import Pin, PWM
import time
import micropython
class StepperMotor:
    def __init__(self, pins, step_mode="FULL", pwm_pct=15, frequency=16_000, micro_steps=32, steps_per_rev=200):
        """
        Initialize the stepper motor with given pins, PWM frequency, step mode, and steps per revolution.
        
        :param pins: List of GPIO pin numbers connected to the motor driver.
        :param step_mode: The stepping mode for the motor ("FULL", "HALF", or "MICRO").
        :param pwm_pct: PWM percentage for each motor coil (0 to 100).
        :param frequency: Frequency for the PWM signals in Hz.
        :param micro_steps: Number of micro-steps per full step (used in micro-stepping mode).
        :param [TODO: Implement RPM] steps_per_rev: Number of steps required for one full revolution (default is 200).
        """

        # Initialize PWM for each pin
        self.pins = [PWM(Pin(pin)) for pin in pins]
        
        # Motor parameters
        self.steps_per_rev = steps_per_rev  # Steps per revolution 

        # Set the PWM frequency for all pins
        self.set_frequency(frequency)
 
        # Calculate the PWM value from percentage (65535 is max for 16-bit)
        self.pwm_max = 65535
        self.pwm_val = int(self.pwm_max * pwm_pct / 100)
        self.micro_steps = micro_steps
        self.step_mode = step_mode.upper() # Ensure that is it uppercase letters
        
        # Initialize step counter to track the total number of step sequences
        self.step_counter = 0

        # Choose the step sequence based on the mode (FULL, HALF, or MICRO)
        if self.step_mode == "FULL":
            # Full-step sequence
            self.step_sequence = [
                [self.pwm_val, self.pwm_val, 0, 0],
                [0, self.pwm_val, self.pwm_val, 0],
                [0, 0, self.pwm_val, self.pwm_val],
                [self.pwm_val, 0, 0, self.pwm_val],
            ]
        elif self.step_mode == "HALF":
            # Half-step sequence
            self.step_sequence = [
                [self.pwm_val, 0, 0, 0],
                [self.pwm_val, self.pwm_val, 0, 0],
                [0, self.pwm_val, 0, 0],
                [0, self.pwm_val, self.pwm_val, 0],
                [0, 0, self.pwm_val, 0],
                [0, 0, self.pwm_val, self.pwm_val],
                [0, 0, 0, self.pwm_val],
                [self.pwm_val, 0, 0, self.pwm_val]
            ]
        elif self.step_mode == "MICRO":
            # Generate micro-stepping sequence
            self.step_sequence = self.generate_micro_step_sequence(self.pwm_val, self.micro_steps)
        
        else:
            # Invalid step mode handling
            self.stop_sequence = [0, 0, 0, 0]
            raise ValueError("Invalid step mode! Use 'FULL', 'HALF', or 'MICRO'.")
        
        # Print the step sequence for debugging purposes
        #self.print_step_sequence()
        
        # Sequence to stop the motor (no current in coils)
        self.stop_sequence = [0, 0, 0, 0]
        self._running = False
        
    def set_microsteps(self, microsteps):
        self.step_sequence = self.generate_micro_step_sequence(self.pwm_val, microsteps)

    def generate_micro_step_sequence(self, pwm_val, micro_steps):
        """
        Generates a step sequence for micro-stepping where PWM values increase and decrease alternately.
        
        :param pwm_val: Maximum PWM value for 16-bit resolution (65535).
        :param micro_steps: Number of micro-steps per full step.
        
        :return: A list of lists representing the step sequence for micro-stepping.
        """
        micro_step_size = pwm_val // micro_steps  # Define the micro step size
        step_sequence = []

        # Generate the step sequence for each phase
        # Phase 1: PWM on first pin, decreasing; PWM on second pin, increasing
        for i in range(micro_steps):
            pwm_1 = pwm_val - i * micro_step_size
            pwm_2 = i * micro_step_size
            step_sequence.append([pwm_1, pwm_2, 0, 0])

        # Phase 2: PWM on second pin, decreasing; PWM on third pin, increasing
        for i in range(micro_steps):
            pwm_2 = pwm_val - i * micro_step_size
            pwm_3 = i * micro_step_size
            step_sequence.append([0, pwm_2, pwm_3, 0])

        # Phase 3: PWM on third pin, decreasing; PWM on fourth pin, increasing
        for i in range(micro_steps):
            pwm_3 = pwm_val - i * micro_step_size
            pwm_4 = i * micro_step_size
            step_sequence.append([0, 0, pwm_3, pwm_4])

        # Phase 4: PWM on fourth pin, decreasing; PWM on first pin, increasing
        for i in range(micro_steps):
            pwm_4 = pwm_val - i * micro_step_size
            pwm_1 = i * micro_step_size
            step_sequence.append([pwm_1, 0, 0, pwm_4])

        return step_sequence

    def set_frequency(self, frequency):
        """
        Set the frequency for the PWM signals.

        :param frequency: The frequency of the PWM signal in Hz.
        """
        # Apply the given frequency to all pins
        for pin in self.pins:
            pin.freq(frequency)

    def stop_running(self):
        """
        Stop the continuous running of the stepper motor.
        """
        self._running = False  # Set running flag to False
        self.stop()  # Stop the motor

    def stop(self):
        """
        Set all PWM outputs to 0 to stop the motor.
        """
        self.set_step(self.stop_sequence)  # Apply stop sequence
    
    @micropython.native
    def set_step(self, step):
        """
        Set the stepper motor to a specific step.
 
        :param step: A list representing the step sequence.
        """
        # Apply the PWM values to each pin for the current step
        for pin in range(len(self.pins)):
            self.pins[pin].duty_u16(step[pin])

from machine import Pin, PWM
import time

class StepperMotor:
    def __init__(self, pins, step_mode="FULL", pwm_pct=20, frequency=16_000, micro_steps=32, steps_per_rev=200):
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
                [self.pwm_val, 0, 0, self.pwm_val]
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
    
    def set_speed(self, pwm_pct, adjusted_microsteps, mode):
        self.pwm_val = int(self.pwm_max * pwm_pct / 100)
        #print(self.pwm_val)
        if mode == "FULL":
            # Full-step sequence
            self.step_sequence = [
                [self.pwm_val, self.pwm_val, 0, 0],
                [0, self.pwm_val, self.pwm_val, 0],
                [0, 0, self.pwm_val, self.pwm_val],
                [self.pwm_val, 0, 0, self.pwm_val]
            ]
        elif mode == "HALF":
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
        elif mode == "MICRO":
            # Generate micro-stepping sequence
            self.step_sequence = self.generate_micro_step_sequence(self.pwm_val, adjusted_microsteps)
        
        else:
            # Invalid step mode handling
            self.stop_sequence = [0, 0, 0, 0]
            raise ValueError("Invalid step mode! Use 'FULL', 'HALF', or 'MICRO'.")
        
    def set_frequency(self, frequency):
        """
        Set the frequency for the PWM signals.

        :param frequency: The frequency of the PWM signal in Hz.
        """
        # Apply the given frequency to all pins
        for pin in self.pins:
            pin.freq(frequency)
    
    def move_stepper(self, steps, direction, delay_us):
        """
        
        """
        if direction == "forward":
            direction_step = 1
        elif direction == "backward":
            direction_step = -1
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")
    
        steps = abs(steps)

        for _ in range(steps):
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(delay_us)
            
            self.step_counter += direction_step

        self.stop()

    def move_stepper_with_ramp(self, steps, direction, initial_delay_us=2000, final_delay_us=1000, ramp_steps=10):
        """
        Move the stepper motor with a speed ramp-up over a specified number of steps.
        
        :param steps: Number of steps to move.
        :param direction: Direction to move. "forward" for forward, "backward" for backward.
        :param initial_delay_us: Initial delay between steps in microseconds (for ramp-up start).
        :param final_delay_us: Final delay between steps in microseconds (for full speed).
        :param ramp_steps: Number of steps to use for ramping up/down.
        """
        # Determine direction of movement
        if direction == "forward":
            direction_step = 1
        elif direction == "backward":
            direction_step = -1
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")
        
        # Move the motor step by step with ramping up speed
        steps = abs(steps)
        delay_increment = (initial_delay_us - final_delay_us) / ramp_steps  # Calculate delay decrement per ramp step
        
        # Ramp-up phase
        for i in range(ramp_steps):
            delay_us = initial_delay_us - i * delay_increment
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(int(delay_us))  # Apply delay and cast to int
    
        # Full-speed phase
        for _ in range(steps - 2 * ramp_steps):
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(final_delay_us)  # Apply full-speed delay
    
        # Ramp-down phase
        for i in range(ramp_steps):
            delay_us = final_delay_us + i * delay_increment
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(int(delay_us))  # Apply delay and cast to int
    
        self.stop()  # Stop the motor after completing the steps


    def ramp_up(self, steps, direction, initial_delay_us=2000, final_delay_us=1000, ramp_steps=10):
        """
        Move the stepper motor with a speed ramp-up over a specified number of steps, then continue at a steady speed.
        
        :param steps: Number of steps to move.
        :param direction: Direction to move. "forward" for forward, "backward" for backward.
        :param ramp_steps: Number of steps to use for ramping up to full speed.
        :param initial_delay_us: Initial delay between steps in microseconds (for ramp-up start).
        :param final_delay_us: Final delay between steps in microseconds (for full speed).
        """
        # Determine direction of movement
        if direction == "forward":
            direction_step = 1
        elif direction == "backward":
            direction_step = -1
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")
        
        # Calculate delay decrement per ramp step
        delay_increment = (initial_delay_us - final_delay_us) / ramp_steps
        
        # Ramp-up phase
        for i in range(ramp_steps):
            delay_us = initial_delay_us - i * delay_increment
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(int(delay_us))  # Apply delay and cast to int

        # Steady-speed phase
        remaining_steps = steps - ramp_steps
        for _ in range(remaining_steps):
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(final_delay_us)  # Continue with final steady speed delay

        # Stop the motor after completing all steps, 
        # in case that no command is followed by this 
        self.stop()

    def ramp_down(self, steps, direction, initial_delay_us=2000, final_delay_us=1000, ramp_steps=10):
        """
        Move the stepper motor with a speed ramp-up over a specified number of steps.
        
        :param steps: Number of steps to move.
        :param direction: Direction to move. "forward" for forward, "backward" for backward.
        :param ramp_steps: Number of steps to use for ramping down from full speed.
        :param initial_delay_us: Initial delay between steps in microseconds (for ramp-up start).
        :param final_delay_us: Final delay between steps in microseconds (for full speed).
        """
        # Determine direction of movement
        if direction == "forward":
            direction_step = 1
        elif direction == "backward":
            direction_step = -1
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")
        
        # Move the motor step by step with ramping up speed
        steps = abs(steps)
        delay_increment = (initial_delay_us - final_delay_us) / ramp_steps  # Calculate delay decrement per ramp step
    
        # Full-speed phase
        for _ in range(steps - ramp_steps):
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(final_delay_us)  # Apply full-speed delay
    
        # Ramp-down phase
        for i in range(ramp_steps):
            delay_us = final_delay_us + i * delay_increment
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(int(delay_us))  # Apply delay and cast to int
    
        self.stop()  # Stop the motor after completing the steps

    def print_step_sequence(self):
        """
        Print the current step sequence in a structured way.
        """

        # Print each step in the step sequence for debugging / validation
        print("--- Step Sequence ---")
        for idx, step in enumerate(self.step_sequence):
            print(f"Step {idx + 1}: {step}")
        print("-----    End    -----")

    def run_continuously(self, direction, delay_us=1000):
        """
        Run the stepper motor continuously in the specified direction.
        
        :param direction: Direction to move. "forward" for forward, "backward" for backward.
        :param delay_us: Delay between steps in microseconds.
        """
        # Determine direction of movement
        if direction == "forward":
            direction_step = 1
        elif direction == "backward":
            direction_step = -1
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")
        
        # Run the motor until stopped
        self._running = True
        
        while self._running:
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(delay_us)  # Use microsecond delay
            
            self.step_counter += direction_step

    def run_continuously_in_secs(self, direction, seconds, delay_us=1000):
        """
        Run the stepper motor continuously in the specified direction for a set number of seconds.
        
        :param direction: Direction to move. "forward" for forward, "backward" for backward.
        :param seconds: Number of seconds to run the motor.
        :param delay_us: Delay between steps in microseconds.
        """
        # Determine direction of movement
        if direction == "forward":
            direction_step = 1
        elif direction == "backward":
            direction_step = -1
        else:
            raise ValueError("Direction must be 'forward' or 'backward'")
        
        start_time = time.time()  # Track the start time
        self._running = True

        print(f"Running the motor for {seconds} seconds.")
        
        # Run the motor for the specified duration
        while time.time() - start_time < seconds:
            for step in range(len(self.step_sequence))[::direction_step]:
                self.set_step(self.step_sequence[step])
                time.sleep_us(delay_us)  # Use microsecond delay
            
            self.step_counter += direction_step
        
        self.stop_running()
        print(f"Motor stopped after {seconds} seconds.")

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

    def set_step(self, step):
        """
        Set the stepper motor to a specific step.
 
        :param step: A list representing the step sequence.
        """
        # Apply the PWM values to each pin for the current step
        for pin in range(len(self.pins)):
            self.pins[pin].duty_u16(step[pin])



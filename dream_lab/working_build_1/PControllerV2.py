import micropython
class PController:
    def __init__(self, Kp, normal_pwm, normal_hastighed, max_pwm, max_hastighed, weights):
        """
        Initialize the stepper motor with given pins, PWM frequency, step mode, and steps per revolution.
        
        param: Kp: Proportional gain
        param: normal_pwm: Base PWM value for motors
        param: normal_hastighed: Base speed for motors
        param: max_pwm: Maximum PWM allowed
        param: max_hastighed: Maximum speed allowed
        param: weights: Weighting factors for each sensor (list or tuple)
        """
        self.Kp = Kp
        self.normal_pwm = normal_pwm
        self.max_pwm = max_pwm
        self.weights = weights  
        self.normal_hastighed = normal_hastighed
        self.max_hastighed = max_hastighed
    
    @micropython.native # Optimization of function for microcontroller speed
    def beregn_control(self, sensor_values):
        """
        Calculate motor PWM and speed values based on sensor readings.
        
        param: sensor_values: List of readings from sensors
        
        Returns: (left_pwm, right_pwm, left_speed, right_speed)
        """
        total = 0
        weighted = 0
        weights = self.weights

        # Finds the weighted sums of the sensor values
        for i in range(len(weights)):
            s = sensor_values[i]
            total += s
            weighted += s * weights[i]
        
        # Calculate the proportional error.
        # We calculate how far off-center we are from the line.
        if total:
            error = weighted / total
        else:
            error = 0
        # Calculate how much we need to turn left or right. 
        steering = self.Kp * error
        max_pwm = self.max_pwm

        # We ensure that the motor doesn't exceed the set PWM
        if steering > max_pwm:
            steering = max_pwm
        elif steering < -max_pwm:
            steering = -max_pwm

        normal_pwm = self.normal_pwm
        
        left_pwm = normal_pwm + steering
        left_pwm = min(max(left_pwm, 0), max_pwm)  # Clamp to [0, max_pwm]
        
        right_pwm = normal_pwm - steering
        right_pwm = min(max(right_pwm, 0), max_pwm)  # Clamp to [0, max_pwm]

        # Calculates speed adjustment based on the turning value
        if steering >= 0:
            turn_effect = steering / max_pwm
            left_speed = self.normal_hastighed * (1 - turn_effect)
            right_speed = self.normal_hastighed
        else:
            turn_effect = (-steering) / max_pwm
            left_speed = self.normal_hastighed
            right_speed = self.normal_hastighed * (1 - turn_effect)

        max_speed = self.max_hastighed

        if left_speed < 0:
            left_speed = 0
        elif left_speed > max_speed:
            left_speed = max_speed

        if right_speed < 0:
            right_speed = 0
        elif right_speed > max_speed:
            right_speed = max_speed
        
        # Return PWM and speed for both motors
        return (
            left_pwm,
            right_pwm,
            int(left_speed),
            int(right_speed),
        )

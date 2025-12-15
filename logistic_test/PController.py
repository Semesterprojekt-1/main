class PController:
    def __init__(self, Kp, normal_pwm, normal_hastighed, max_pwm, max_hastighed, weights):
        self.Kp = Kp
        self.normal_pwm = normal_pwm
        self.max_pwm = max_pwm
        self.weights = weights
        self.normal_hastighed = normal_hastighed
        self.max_hastighed = max_hastighed

    def beregn_position(self, sensor_values):
        total = sum(sensor_values)
        if total == 0:
            return 0
        return sum(s * w for s, w in zip(sensor_values, self.weights)) / total

    def beregn_control(self, sensor_values):
        error = self.beregn_position(sensor_values)

        # steering force ONLY
        steering = self.Kp * error
        steering = max(-self.max_pwm, min(self.max_pwm, steering))

        # PWM control
        left_pwm  = self.normal_pwm + steering
        right_pwm = self.normal_pwm - steering

        left_pwm  = max(0, min(self.max_pwm, left_pwm))
        right_pwm = max(0, min(self.max_pwm, right_pwm))

        # SPEED control (constant forward speed)
        # Turning only reduces one wheel speed, it does NOT use error directly
        turn_effect = abs(steering) / self.max_pwm  # 0 to 1

        left_speed  = self.normal_hastighed * (1 - turn_effect) if steering > 0 else self.normal_hastighed
        right_speed = self.normal_hastighed * (1 - turn_effect) if steering < 0 else self.normal_hastighed

        # clamp
        left_speed  = int(max(0, min(self.max_hastighed, left_speed)))
        right_speed = int(max(0, min(self.max_hastighed, right_speed)))

        return left_pwm, right_pwm, left_speed, right_speed


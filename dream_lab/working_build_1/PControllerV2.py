import micropython
class PController:
    def __init__(self, Kp, normal_pwm, normal_hastighed, max_pwm, max_hastighed, weights):
        self.Kp = Kp
        self.normal_pwm = normal_pwm
        self.max_pwm = max_pwm
        self.weights = weights  # MUST be a fixed tuple or list
        self.normal_hastighed = normal_hastighed
        self.max_hastighed = max_hastighed
    @micropython.native
    def beregn_control(self, sensor_values):
        total = 0
        weighted = 0
        weights = self.weights

        # Manual index loop avoids zip object creation
        for i in range(len(weights)):
            s = sensor_values[i]
            total += s
            weighted += s * weights[i]

        if total:
            error = weighted / total
        else:
            error = 0

        steering = self.Kp * error
        max_pwm = self.max_pwm

        if steering > max_pwm:
            steering = max_pwm
        elif steering < -max_pwm:
            steering = -max_pwm

        normal_pwm = self.normal_pwm

        left_pwm = normal_pwm + steering
        if left_pwm < 0:
            left_pwm = 0
        elif left_pwm > max_pwm:
            left_pwm = max_pwm

        right_pwm = normal_pwm - steering
        if right_pwm < 0:
            right_pwm = 0
        elif right_pwm > max_pwm:
            right_pwm = max_pwm

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

        return (
            left_pwm,
            right_pwm,
            int(left_speed),
            int(right_speed),
        )

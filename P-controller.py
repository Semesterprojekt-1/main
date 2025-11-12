# Vi har en klasse med vores hældningskoefficient (Kp) og andrwe vigtige værdier som input
class PController:
    def __init__(self, Kp, normal_hastighed, max_pwm, weights):
        """
        Kp: proportional gain
        base_speed: base PWM for straight movement
        max_pwm: maximum PWM allowed (for testing)
        weights: list of weights for each sensor
        """
        self.Kp = Kp
        self.normal_hastighed = normal_hastighed
        self.max_pwm = max_pwm
        self.weights = weights

    def beregn_position(self, sensor_values):
        # Funktionen beregner hvor robotten er på linje. 
        # position = 0 => vi er på linjen. position < 0 => linjen er til venstre. position > 0 => linjen er til højre
        total = sum(sensor_values)
        if total == 0:
            return 0  # For at fohindre 0 division
        position = sum(s * w for s, w in zip(sensor_values, self.weights)) / total
        return position

    def beregn_control(self, sensor_values):
        # Vi beregner nu fejlen. Jo større en fejl, desto større en korrektion :D
        error = self.beregn_position(sensor_values)
        steering = self.Kp * error

        # Vi sætter max PWM til vores input værdi
        steering = max(-self.max_pwm, min(self.max_pwm, steering))

        left_pwm = self.normal_hastighed + steering
        right_pwm = self.normal_hastighed - steering

        # Sikrer at vi ikke går under PWM = 0
        left_pwm = max(0, min(self.max_pwm, left_pwm))
        right_pwm = max(0, min(self.max_pwm, right_pwm))

        return int(left_pwm), int(right_pwm)


"""
Eksempel
weights = [-2, -1, 0, 1, 2]

controller = PController(Kp=0.5, normal_hastighed=15, max_pwm=20, weights=weights)


while True:
    # Læs værdier fra multiplexer på en eller anden måde 
    sensors = [read_sensor(i) for i in range(5)]

    #beregn PWM med P-klassen
    left_pwm, right_pwm = controller.beregn_position(sensors)

    # Sæt PWM - vi skal have skrevet koden til det. 
    motor_left.duty_u16(left_pwm)
    motor_right.duty_u16(right_pwm)

"""
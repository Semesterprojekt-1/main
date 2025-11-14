# Vi har en klasse med vores hældningskoefficient (Kp) og andrwe vigtige værdier som input
import uasyncio as asyncio

class PController:
    def __init__(self, Kp, normal_pwm, normal_hastighed, max_pwm, max_hastighed, weights):
        """
        Kp: proportional gain INT
        base_speed: base PWM for straight movement INT
        max_pwm: maximum PWM allowed (for testing) INT
        weights: list of weights for each sensor LIST
        """
        self.Kp = Kp
        self.normal_pwm = normal_pwm
        self.max_pwm = max_pwm
        self.weights = weights
        self.max_hastighed = max_hastighed

        self.normal_hastighed = normal_hastighed
        
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
        #print(error)
        
        steering = self.Kp * error
        speed = self.Kp * error
        
        # Vi sætter max PWM til vores input værdi
        steering = max(-self.max_pwm, min(self.max_pwm, steering))
        speed = max(-self.max_hastighed, min(self.max_hastighed, speed))
        
        left_pwm = self.normal_pwm + steering
        right_pwm = self.normal_pwm - steering
        
        left_speed = self.normal_hastighed + speed
        right_speed = self.normal_hastighed - speed

        
        # Sikrer at vi ikke går under PWM = 0
        left_pwm = round(max(0, min(self.max_pwm, left_pwm)),2)
        right_pwm = round(max(0, min(self.max_pwm, right_pwm)),2)
        
        left_speed = max(0, min(self.max_hastighed, left_speed))
        right_speed = max(0, min(self.max_hastighed, right_speed))
        
        #print(left_pwm,right_pwm)
        return left_pwm, right_pwm, int(left_speed), int(right_speed)

# from machine import Pin,ADC
# import time
# 
# def select_channel(ch):
#     if ch < 0 or ch > 7:
#         raise ValueError("Channel must be 0–7")
#     S0.value(ch & 0x01) #Converts number to binary and sets s0 to the last bit value
#     S1.value((ch >> 1) & 0x01) #Converts number to binary and sets s1 to the second last bit value
#     S2.value((ch >> 2) & 0x01) #Converts number to binary and sets s2 to the third last bit value
#     time.sleep(0.002)        
#         
# def read_channel(ch):
#     select_channel(ch)
#     return adc.read_u16()
# 
# 
# #Eksempel
# weights = [-2, -1, 0, 1, 2]
# 
# 
# controller = PController(Kp=0.5, normal_hastighed=15, max_pwm=20, weights=weights)
# 
# S0=Pin(8,Pin.OUT)
# S1=Pin(9,Pin.OUT)
# S2=Pin(10,Pin.OUT)
# adc = ADC(26)
# 
# 
# 
# while True:
#     # Læs værdier fra multiplexer på en eller anden måde 
#     sensors = []
#     for ch in range(5):
#         sensors.append(read_channel(ch))
# 
#     #beregn PWM med P-klassen
#     left_pwm, right_pwm = controller.beregn_control(sensors)
#     
#     print (sensors)
# 
#     time.sleep(0.5)
# 
#     # Sæt PWM - vi skal have skrevet
#     
#     


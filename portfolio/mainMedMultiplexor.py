from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from SaveData import SaveData
from machine import Timer, ADC, Pin
import time
# Setup
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]
S0=Pin(8,Pin.OUT)
S1=Pin(9,Pin.OUT)
S2=Pin(10,Pin.OUT)

# Variables for motors
pwm = 20
frekvens = 16000
microsteps = 80
steps_per_rev = 200

# Stepper motor instances
left = StepperMotor(pins_left, "MICRO", pwm, frekvens, microsteps, steps_per_rev)
right = StepperMotor(pins_right, "MICRO", pwm, frekvens, microsteps, steps_per_rev)

# Differential drive instance
diff = DifferentialDrive(left, right)

def DataCollection(timer):
    global voltageList
    volt=3.3*(adc.read_u16()/65535)
    voltageList.append(volt)
    #print("Voltage: {}V ".format(volt))
    
def select_channel(ch):
    if ch < 0 or ch > 7:
        raise ValueError("Channel must be 0–7")
    S0.value(ch & 0x01) #Converts number to binary and sets s0 to the last bit value
    S1.value((ch >> 1) & 0x01) #Converts number to binary and sets s1 to the second last bit value
    S2.value((ch >> 2) & 0x01) #Converts number to binary and sets s2 to the third last bit value
    time.sleep(0.002)        
        
def read_channel(ch):
    select_channel(ch)
    return adc.read_u16()
    
# Run
if __name__ == "__main__":
    time.sleep(2)
    
    voltageList =[]
    adc = ADC(26)
    timer = Timer()
    timer.init(freq=10,mode=Timer.PERIODIC,callback=DataCollection)
    
    diff.turn_in_place("right", 180)
    time.sleep(2)
    diff.turn_in_place("left", 180)
    timer.deinit()
    SaveData(voltageList)
    print(voltageList)
    

    



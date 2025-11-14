# Import classes
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import Timer, ADC, Pin
from PController import PController

# Import necessary libraries
import time
import uasyncio as asyncio


# Setup
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]
S0=Pin(8,Pin.OUT)
S1=Pin(9,Pin.OUT)
S2=Pin(10,Pin.OUT)
adc=ADC(26)

# Define left and right stepper motor instances with MICRO stepping as selected mode.

pwm = 20
frekvens = 18000
micro_steps = 80
steps_pr_rev = 200

left = StepperMotor(pins_left, "MICRO", pwm, frekvens, micro_steps, steps_pr_rev)
right = StepperMotor(pins_right, "MICRO", pwm, frekvens, micro_steps, steps_pr_rev)

# Define differentialdrive instance
diff = DifferentialDrive(left, right)

# Define P-controller variables
weights = [-2.5, -1, 0, 1, 2.5]
Kp = 75
normal_pwm = 30
normal_hastighed = 20
max_pwm = 30
max_hastighed = 12

# Define P-controller instance
controller = PController(Kp, normal_pwm, normal_hastighed, max_pwm, max_hastighed, weights)

# Set the speed and pwm to default values
left_pwm, right_pwm, left_speed, right_speed = normal_pwm, normal_pwm, normal_hastighed, normal_hastighed

# Read data from multiplexer and LDR-array   
def select_channel(ch):
    if ch < 0 or ch > 7:
        raise ValueError("Channel must be 0–7")
    S0.value(ch & 0x01) #Converts number to binary and sets s0 to the last bit value
    S1.value((ch >> 1) & 0x01) #Converts number to binary and sets s1 to the second last bit value
    S2.value((ch >> 2) & 0x01) #Converts number to binary and sets s2 to the third last bit value
        
def read_channel(ch):
    select_channel(ch)
    return adc.read_u16()


#----------Sensor Task----------
async def sensor_task():
    global left_pwm, right_pwm, left_speed, right_speed

    while True:
        sensors = [read_channel(ch) for ch in range(5)]
        #print(sensors)
        left_pwm, right_pwm, left_speed, right_speed = controller.beregn_control(sensors)
        
        await asyncio.sleep_ms(20)
        
#----------Move robot---------
async def move_robot():
    global left_pwm, right_pwm, left_speed, right_speed
    while True:
        if left_speed == right_speed:
            diff.set_speed(left_pwm, right_pwm, left_speed, right_speed, "HALF")
            diff.backward("HALF")
        else:
            diff.set_speed(left_pwm, right_pwm, left_speed, right_speed, "MICRO")
            diff.backward("MICRO")
        
        await asyncio.sleep(0.0001)        

#----------main loop----------
async def main():
    asyncio.create_task(sensor_task())
    asyncio.create_task(move_robot())
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
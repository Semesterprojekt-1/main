from stepper_motor import StepperMotor
from differential_drive import DifferentialDrive
from machine import ADC,Pin
import time
import math

pins_right = [0,1,2,3]
pins_left = [4,5,6,7]

left = StepperMotor(pins_left, "MICRO", 20, 16000, 32, 200)
right = StepperMotor(pins_right, "MICRO", 20, 16000, 32, 200)
diff = DifferentialDrive(left, right)


adcX = ADC(26)
adcY = ADC(27)
Freq=0

while True:
    valueX = adcX.read_u16()
    valueY = adcY.read_u16()
    '''if valueY-51000<0:
        Freq=(valueY-51000)/24000*100
    else:
        Freq=(valueY-51000)/14000*100'''
    if valueY >= 51000:
        diff.forward(4)
    elif valueY <= 49000:
        diff.backward(4)
    elif valueX >= 51000:
        diff.turn_in_place("left", 3)
    elif valueX <= 49000:
        diff.turn_in_place("right", 3)
   
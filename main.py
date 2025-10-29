from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from SaveData import SaveData
from machine import Timer, ADC
import time
# Setup
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]

left = StepperMotor(pins_left, "MICRO", 20, 16000, 80, 200)
right = StepperMotor(pins_right, "MICRO", 20, 16000, 80, 200)

diff = DifferentialDrive(left, right)

def DataCollection(timer):
    global voltageList
    digital_value = adc.read_u16()
    volt=3.3*(digital_value/65535)
    voltageList.append(volt)
    #print("Voltage: {}V ".format(volt))
    
# Run
if __name__ == "__main__":
    #time.sleep(5)
    voltageList =[]
    adc = ADC(28)
    timer = Timer()
    timer.init(freq=10,mode=Timer.PERIODIC,callback=DataCollection)
    
    
    diff.turn_in_place("right", 180)
    time.sleep(2)
    diff.turn_in_place("left", 180)
    timer.deinit()
    SaveData(voltageList)
    #print(voltageList)
    

from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from SaveData import SaveData
from machine import Timer, ADC, Pin
import time
# Setup
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]
light = Pin("GP8", Pin.OUT)
sensorL = ADC(27)
sensorR = ADC(28)

left = StepperMotor(pins_left, "MICRO", 20, 16000, 12, 200)
right = StepperMotor(pins_right, "MICRO", 20, 16000, 12, 200)

diff = DifferentialDrive(left, right)

def DataCollection(timer):
    global voltageList
    digital_value1 = sensorL.read_u16()
    digital_value2 = sensorR.read_u16()
    volt=3.3*(digital_value1/65535)
    volt=3.3*(digital_value2/65535)

    voltageList.append(volt)
    #print("Voltage: {}V ".format(volt))
    



def Bangbang():
    while True:
        if 3.3*(sensorL.read_u16()/65535) > 2.7: #if left sensor reads higher than 2.7 then its white    
            while True:
                diff.turn_degrees_back("right", 3)
                if 3.3*(sensorL.read_u16()/65535) < 2.7: #if the left sensor reads lower than 2.7 then its black and it will follow the line 
                    break
        elif 3.3*(sensorR.read_u16()/65535) > 2.7: # if right sensor reads higher than 2.7 then its white  
            while True:
                diff.turn_degrees_back("left", 3)  
                if 3.3*(sensorR.read_u16()/65535) < 2.7:
                    break
        else:
            diff.backward(3)
   
        
        
    
    
    
# Run
if __name__ == "__main__":
    #time.sleep(5)
    #voltageList =[]
    #adc = ADC(28)
    light.on()
    #timer = Timer()
    #timer.init(freq=10,mode=Timer.PERIODIC,callback=DataCollection)
    
    
    Bangbang()
    #timer.deinit()
    #SaveData(voltageList)
    #print(voltageList)

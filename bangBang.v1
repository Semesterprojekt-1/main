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

left = StepperMotor(pins_left, "MICRO", 20, 16000, 32, 200)
right = StepperMotor(pins_right, "MICRO", 20, 16000, 32, 200)

diff = DifferentialDrive(left, right)

def DataCollection(timer):
    global voltageList
    digital_value1 = sensorL.read_u16()
    digital_value2 = sensorR.read_u16()
    voltL=3.3*(digital_value1/65535)
    voltR=3.3*(digital_value2/65535)

    voltageList.append(voltL, voltR)
    #print("Voltage: {}V ".format(volt))
    



def Bangbang():
    while True:
        if 3.3*(sensorL.read_u16()/65535) > 2.4 and 3.3*(sensorR.read_u16()/65535) < 2.4: #if left sensor reads higher than 2.7 then its white    
            diff.turn_degrees_back("right", 3)
        elif 3.3*(sensorR.read_u16()/65535) > 2.4 and 3.3*(sensorL.read_u16()/65535) < 2.4: # if right sensor reads higher than 2.7 then its white  
            diff.turn_degrees_back("left", 3)
        else:
            diff.backward(3)
        #print(f"L: {3.3*(sensorL.read_u16()/65535)}")
        #print(f"R: {3.3*(sensorR.read_u16()/65535)}")


# Run
if __name__ == "__main__":
    #time.sleep(5)
    #voltageList =[]
    #adc = ADC(28)
    light.on()
    #timer = Timer()
    #timer.init(freq=10,mode=Timer.PERIODIC,callback=DataCollection)
    print(f"L: {3.3*(sensorL.read_u16()/65535)}")
    print(f"R: {3.3*(sensorR.read_u16()/65535)}")
    Bangbang()
    #timer.deinit()
    #SaveData(voltageList)
    #print(voltageList)

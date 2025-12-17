from machine import UART, Pin, ADC
from stepper_motor_new import StepperMotor
from small_stepper_motor import SmallStepperMotor
from Small_Differential_Drive import SmallDifferentialDrive
from Main_kran import base_move, base_lock
import utime
import time

magnet = Pin(9,Pin.OUT)

gearPins = [14,15,18,19]
left = SmallStepperMotor(gearPins, delay_ms=15)

magnetPins = [10,11,22,26]
right = SmallStepperMotor(magnetPins, delay_ms=5)          

diff = SmallDifferentialDrive(left, right)

rightADC = ADC(28)
leftADC = ADC(27)

uart = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13))
rCounter=0


# if __name__ == "__main__":
#     base_move(10, "right", 2)
#     time.sleep(1)
#     base_move(10, "left", 2)
base_lock("off")
magnet.off()
while True:
    rightV = rightADC.read_u16()
    leftV = leftADC.read_u16()
#     print("left", leftV)
#     print("right", rightV)
#     time.sleep(0.2)
#     print(rCounter,lCounter)
#     time.sleep(0.2)
    
    
    
    if rightV < 30000:
        uart.write(str("r"))
        print("r")
        rCounter+=1
        time.sleep(2)
        
               

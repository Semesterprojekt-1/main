from stepper_motor_new import StepperMotor
from machine import Pin
import time

basePins = [0,1,2,3]
base = StepperMotor(basePins, "MICRO", 100, 16000, 20, 200)

def base_move(steps, direction, wait):
    if direction == "left":
        if steps > 25:
            print("Too many steps. Max is 25")
        elif steps <= 0:
            print("Too few steps. Min is 1")
        else:
            base.move_stepper(steps, "forward", 200)
            time.sleep(wait)
            base.stop()
    elif direction == "right":
        if steps > 25:
            print("Too many steps. Max is 25")
        elif steps <= 0:
            print("Too few steps. Min is 1")
        else:
            base.move_stepper(steps, "backward", 200)
            time.sleep(wait)
            base.stop()
def base_lock(status):
    if status == "on":
        base.set_step([1, 1, 1, 1])
    elif status == "off":
        base.stop()
        

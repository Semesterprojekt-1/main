# Import classes
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import ADC, Pin
from PController import PController
import time
import uasyncio as asyncio

# --- Setup pins ---
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]
S0 = Pin(8, Pin.OUT)
S1 = Pin(9, Pin.OUT)
S2 = Pin(10, Pin.OUT)
adc = ADC(26)

# --- Stepper motor setup (HALF step mode) ---
pwm = 30
frequency = 18000
micro_steps = 80
steps_per_rev = 200

left = StepperMotor(pins_left, "FULL", pwm, frequency, micro_steps, steps_per_rev)
right = StepperMotor(pins_right, "FULL", pwm, frequency, micro_steps, steps_per_rev)

# --- Differential drive ---
diff = DifferentialDrive(left, right)

# --- P-controller ---
#weights = [-2, -1, 0, -5, 2, 5, 1]
weights = [-5, -3, -2, 0, 1, 3, 5]
Kp = 100
normal_pwm = 30
normal_speed = 8
max_pwm = 40
max_speed = 24

controller = PController(Kp, normal_pwm, normal_speed, max_pwm, max_speed, weights)

left_speed = normal_speed
right_speed = normal_speed


def select_channel(ch):
    S0.value(ch & 1)
    S1.value((ch >> 1) & 1)
    S2.value((ch >> 2) & 1)

def read_channel(ch):
    select_channel(ch)
    return adc.read_u16()


async def sensor_task():
    global left_speed, right_speed

    while True:
        # Read sensors
        sensors = [read_channel(ch) for ch in range(7)]
        
        
        right_pwm, left_pwm, right_speed, left_speed = controller.beregn_control(sensors)
        
    
        await asyncio.sleep_ms(5)


# ============================================================
# Move robot
# ============================================================
async def move_robot():
    global left_speed, right_speed

    left_index = 0
    right_index = 0
    left_seq = left.step_sequence
    right_seq = right.step_sequence

    last_time_left = time.ticks_ms()
    last_time_right = time.ticks_ms()

    MAX_STEP_RATE = 2400
    MIN_STEP_RATE = 100

    while True:
        now = time.ticks_ms()

        # Convert speed (0–24) → step rate (200–1500)
        left_step_rate  = MIN_STEP_RATE + int((left_speed  / max_speed) * (MAX_STEP_RATE - MIN_STEP_RATE))
        right_step_rate = MIN_STEP_RATE + int((right_speed / max_speed) * (MAX_STEP_RATE - MIN_STEP_RATE))

        left_delay  = max(1, int(1000 / left_step_rate))
        right_delay = max(1, int(1000 / right_step_rate))

        # Step left motor
        if time.ticks_diff(now, last_time_left) >= left_delay:
            left.set_step(left_seq[left_index])
            left_index = (left_index + 1) % len(left_seq)
            last_time_left = now

        # Step right motor
        if time.ticks_diff(now, last_time_right) >= right_delay:
            right.set_step(right_seq[right_index])
            right_index = (right_index + 1) % len(right_seq)
            last_time_right = now

        await asyncio.sleep_ms(1)


# ============================================================
# Main loop
# ============================================================
async def main():
    asyncio.create_task(sensor_task())
    asyncio.create_task(move_robot())
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())




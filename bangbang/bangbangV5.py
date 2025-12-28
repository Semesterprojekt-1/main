# Import classes
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import ADC, Pin
import time
import uasyncio as asyncio
#45 sek


# --- Setup pins ---
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]
S0 = Pin(8, Pin.OUT)
S1 = Pin(9, Pin.OUT)
S2 = Pin(10, Pin.OUT)
adc = ADC(26)

# --- Stepper motor setup (HALF step mode) ---
pwm = 20
frequency = 18000
micro_steps = 80
steps_per_rev = 200
left = StepperMotor(pins_left, "HALF", pwm, frequency, micro_steps, steps_per_rev)
right = StepperMotor(pins_right, "HALF", pwm, frequency, micro_steps, steps_per_rev)

diff = DifferentialDrive(left, right)

# Bang-bang parameters
THRESHOLD = 30000
BASE_SPEED = 10
TURN_SPEED = 0

left_speed = BASE_SPEED
right_speed = BASE_SPEED

def select_channel(ch):
    S0.value(ch & 1)
    S1.value((ch >> 1) & 1)
    S2.value((ch >> 2) & 1)

def read_channel(ch):
    select_channel(ch)
    return adc.read_u16()


async def bangBang():
    global left_speed, right_speed
    last_print = time.ticks_ms()
    
    while True:
        # Read sensors
        sensors = [read_channel(ch) for ch in range(7)]
        
        # Bang-bang control logic
        # Check center sensor first 
#         if sensors[2] < THRESHOLD:  # Line is centered
#             left_speed = BASE_SPEED
#             right_speed = BASE_SPEED
#             state = "CENTERED"
        
         # Check left and middle sensor
        if sensors[4] < THRESHOLD:
            # Line is on the right - turn right
            left_speed = BASE_SPEED
            right_speed = TURN_SPEED
            state = "TURN RIGHT"
        
        # Check right and middle sensors 
        elif sensors[2] < THRESHOLD:
            # Line is on the left - turn left
            left_speed = TURN_SPEED
            right_speed = BASE_SPEED
            state = "TURN LEFT"
        
        else:
            # No line detected - keep going straight
            left_speed = BASE_SPEED + 4
            right_speed = BASE_SPEED + 4
            state = "NO LINE"
            
        
    
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
    max_speed = 24
    
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
# Main loop - Start both tasks!
# ============================================================
async def main():
    asyncio.create_task(bangBang())
    asyncio.create_task(move_robot())
    while True:
        await asyncio.sleep(1)

# Actually run the event loop!
asyncio.run(main())



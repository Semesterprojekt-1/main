# Import classes
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import ADC, Pin
from PControllerV2 import PController
import time
import _thread
import micropython

# --- Setup pins ---
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]
S0 = Pin(8, Pin.OUT)
S1 = Pin(9, Pin.OUT)
S2 = Pin(10, Pin.OUT)
adc = ADC(26)

# --- Stepper motor setup (HALF step mode) ---
pwm = 55
frequency = 18000
micro_steps = 80
steps_per_rev = 200

left = StepperMotor(pins_left, "FULL", pwm, frequency, micro_steps, steps_per_rev)
right = StepperMotor(pins_right, "FULL", pwm, frequency, micro_steps, steps_per_rev)

# --- Differential drive ---
diff = DifferentialDrive(left, right)

# --- P-controller ---
#weights = [-2, -1, 0, -5, 2, 5, 1]
weights = [-11, -5, -3, 0, 2, 5, 11]
Kp = 55
normal_pwm = 55
normal_speed = 4
max_pwm = 55
max_speed = 12

controller = PController(Kp, normal_pwm, normal_speed, max_pwm, max_speed, weights)

left_speed = normal_speed
right_speed = normal_speed

@micropython.native
def select_channel(ch):
    S0.value(ch & 1)
    S1.value((ch >> 1) & 1)
    S2.value((ch >> 2) & 1)

@micropython.viper
def read_channel(ch):
    select_channel(ch)
    return adc.read_u16()

@micropython.native
def sensor_task():
    global left_speed, right_speed

    while True:
        # Read sensors
        sensors = [read_channel(ch) for ch in range(7)]
        
        
        right_pwm, left_pwm, right_speed, left_speed = controller.beregn_control(sensors)
        
        time.sleep_ms(5)
        

# ============================================================
# Move robot
# ============================================================
@micropython.native
def move_robot():
    global left_speed, right_speed

    left_index = 0
    right_index = 0
    left_seq = left.step_sequence
    right_seq = right.step_sequence

    last_time_left = time.ticks_us()
    last_time_right = time.ticks_us()

    MAX_STEP_RATE = 1800
    MIN_STEP_RATE = 100

    while True:
        now = time.ticks_us()

        # Convert speed (0–24) → step rate (200–1500)
        left_step_rate  = MIN_STEP_RATE + int((left_speed  / max_speed) * (MAX_STEP_RATE - MIN_STEP_RATE))
        right_step_rate = MIN_STEP_RATE + int((right_speed / max_speed) * (MAX_STEP_RATE - MIN_STEP_RATE))

        left_delay  = max(100, int(1000000 / left_step_rate))
        right_delay = max(100, int(1000000 / right_step_rate))
        #print(left_delay,right_delay)
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




# ============================================================
# Main loop
# ============================================================
_thread.start_new_thread(sensor_task, ())
move_robot()   # runs on main core






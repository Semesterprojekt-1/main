# Import classes
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

# Variable setup
pwm = 60
frequency = 18000
micro_steps = 80
steps_per_rev = 200

# Ramping
RAMP_TIME_US = 2_400_000 


left = StepperMotor(pins_left, "FULL", pwm, frequency, micro_steps, steps_per_rev)
right = StepperMotor(pins_right, "FULL", pwm, frequency, micro_steps, steps_per_rev)

# P-controller 
#weights = [-2, -1, 0, -5, 2, 5, 1]
weights = [-3, -2, -1, 0, 1, 2, 3]
Kp = 100
normal_pwm = 60
normal_speed = 4
max_pwm = 100
max_speed = 12

controller = PController(Kp, normal_pwm, normal_speed, max_pwm, max_speed, weights)

left_speed = normal_speed
right_speed = normal_speed

LOG_INTERVAL_MS = 150
RUN_TIME_MS = 15_000

log_buffer = []          # RAM buffer
start_time = time.ticks_ms()
last_log = start_time
running = True

@micropython.native
def select_channel(ch):
    S0.value(ch & 1)
    S1.value((ch >> 1) & 1)
    S2.value((ch >> 2) & 1)

@micropython.viper
def read_channel(ch):
    select_channel(ch)
    return adc.read_u16()

def sensor_task():
    global left_speed, right_speed, last_log, running

    while running:
        sensors = [read_channel(ch) for ch in range(7)]
        left_pwm, right_pwm, left_speed, right_speed = controller.beregn_control(sensors)

        now = time.ticks_ms()

        if time.ticks_diff(now, last_log) >= LOG_INTERVAL_MS:
            total = 0
            weighted = 0
            for i in range(7):
                total += sensors[i]
                weighted += sensors[i] * weights[i]

            error = weighted / total if total else 0

            log_buffer.append((now, error))

            last_log = now

        
        if time.ticks_diff(now, start_time) >= RUN_TIME_MS:
            running = False
            break

        time.sleep_ms(5)


@micropython.native  
def ramp_up():
    global ramp_factor, ramp_done

    for i in range(RAMP_STEPS + 1):
        print(ramp_factor)
        ramp_factor = i / RAMP_STEPS
        time.sleep_ms(RAMP_STEP_MS)

    ramp_factor = 1.0
    ramp_done = True
    if ramp_done:
        return


def move_robot():
    global left_speed, right_speed

    left_index = 0
    right_index = 0
    left_seq = left.step_sequence
    right_seq = right.step_sequence

    last_time_left = time.ticks_us()
    last_time_right = time.ticks_us()

    start_time = time.ticks_us()

    MAX_STEP_RATE = 1800
    MIN_STEP_RATE = 100

    while running:
        now = time.ticks_us()

        dt = time.ticks_diff(now, start_time)

        if dt < RAMP_TIME_US:
            ramp_factor = dt / RAMP_TIME_US
        else:
            ramp_factor = 1.0

        # Apply ramp to speeds
        ls = left_speed * ramp_factor
        rs = right_speed * ramp_factor

        # Convert speed → step rate
        left_step_rate  = MIN_STEP_RATE + int((ls / max_speed) * (MAX_STEP_RATE - MIN_STEP_RATE))
        right_step_rate = MIN_STEP_RATE + int((rs / max_speed) * (MAX_STEP_RATE - MIN_STEP_RATE))

        left_delay  = max(1000, int(1_000_000 / left_step_rate))
        right_delay = max(1000, int(1_000_000 / right_step_rate))

        if time.ticks_diff(now, last_time_left) >= left_delay:
            left.set_step(left_seq[left_index])
            left_index = (left_index + 1) % (len(left_seq))
            last_time_left = now

        if time.ticks_diff(now, last_time_right) >= right_delay:
            right.set_step(right_seq[right_index])
            right_index = (right_index + 1) % (len(right_seq))
            last_time_right = now
            
    
#Main loop
_thread.start_new_thread(sensor_task, ())
move_robot()   # runs on main core
with open("p_log.txt", "w") as f:
    f.write("time_ms,error\n")
    for t, e in log_buffer:
        f.write("{},{}\n".format(t, e))



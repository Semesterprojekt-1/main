from machine import Pin
import time

class SmallStepperMotor:
    sequence = [
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
    [1, 0, 0, 1],
    ]

    step_sequence = sequence

    def __init__(self, pins, delay_ms=5):
        self.pins = [Pin(p, Pin.OUT) for p in pins]
        self.delay = delay_ms
        self.index = 0
        self.sequence = self.step_sequence

    def set_step(self, pattern):
        for pin, val in zip(self.pins, pattern):
            pin.value(val)

    def step(self, steps):
        direction = 1 if steps > 0 else -1
        for _ in range(abs(steps)):
            self.index = (self.index + direction) % len(self.sequence)
            self.set_step(self.sequence[self.index])
            time.sleep_ms(self.delay)

    def stop(self):
        for pin in self.pins:
            pin.value(0)  
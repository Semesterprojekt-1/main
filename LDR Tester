from machine import ADC, Pin
import time

# Setup
light = Pin(8, Pin.OUT)  # GP8
sensorL = ADC(1)         # GP27
sensorR = ADC(0)         # GP26

light.on()

while True:
    digital_value1 = sensorL.read_u16()
    digital_value2 = sensorR.read_u16()
    volt1 = 3.3 * (digital_value1 / 65535)
    volt2 = 3.3 * (digital_value2 / 65535)
    print("Voltage: {:.2f}V, {:.2f}V".format(volt1, volt2))
    time.sleep(0.2)

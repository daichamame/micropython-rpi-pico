"""HC-SR04 sample"""
import daichamame_hcsr04
import time

hcsr04=daichamame_hcsr04.HC_SR04(trig_pin=20,echo_pin=21)
ret=hcsr04.get_data()
print(str(int(ret)) + "mm")

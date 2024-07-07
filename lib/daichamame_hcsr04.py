"""
    HC-SR04 モジュール
    超音波距離センサー
"""
import time
from machine import Pin,time_pulse_us

class HC_SR04():
    # GPIOの設定
    speed = 343.5 # 初期値20℃の時の速度
    def __init__(self,trig_pin,echo_pin,temp=20):
        """ GPIOの設定とスピードの設定"""
        if (trig_pin is not None and echo_pin is not None ):
            self.trig = Pin(trig_pin,Pin.OUT)
            self.echo = Pin(echo_pin,Pin.IN)
            self.trig.value(0)
            self.set_temp(temp)  # 気温から速度の設定

    def get_data(self):
        """ 距離を取得:単位 mm  """
        self.trig.value(0)
        time.sleep_us(5)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        try:
            # 気温0度、測定距離4.5mにかかる時間が27ms　タイムアウトを30msに設定）、
            pulse_time = time_pulse_us(self.echo, 1,30000)
            # 時間をマイクロ秒から秒に変換　戻り値は、ミリメートル 
            return ((self.speed*1000)*(pulse_time/2)/(1000*1000))
        except:
            # 例外発生時
            return -9
    def set_temp(self,temp):
        """ 気温から速度を設定 """
        self.speed = 331.45 + temp*0.6

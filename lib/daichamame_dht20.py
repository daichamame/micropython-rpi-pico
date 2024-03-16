"""
    DHT20
    Humidity and Temperature Module
    I2C Interface
"""
from machine import Pin, I2C
import time

class DHT20(object):
    # I2C
    ADDRESS      = const(0x38)
    def __init__(self):
        # I2Cに使うピンの設定です
        self.i2c = I2C(0,scl=Pin(1),sda=Pin(0),freq=400000)
    def read_status(self):
        ret=self.i2c.readfrom(self.ADDRESS,1)
        return ret
    
    # 初期化処理（リセットを実行）
    def init(self):
        time.sleep_ms(100)
        self.reset()
        time.sleep_ms(100)
        self.reset()
        return self.read_status()

    # リセット
    def reset(self):
        self.i2c.writeto(self.ADDRESS,b'\x1b')
        self.i2c.writeto(self.ADDRESS,b'\x1c')
        self.i2c.writeto(self.ADDRESS,b'\x1e')

    # データを取得
    def get_data(self):
        """ 戻り値：温度、湿度"""
        raw = bytes(7)
        time.sleep_ms(10)
        self.i2c.writeto(self.ADDRESS,b'\xAC\x33\x00')

        time.sleep_ms(80)        
        raw=self.i2c.readfrom(self.ADDRESS,7)
        val = raw[1] << 12
        val += raw[2] << 4
        val += raw[3] >> 4
        hum = val * 100/1048576
        val = (raw[3] & 0x0F) << 16
        val +=raw[4] << 8
        val +=raw[5]
        temp = val * 200/1048576 - 50
        return temp,hum

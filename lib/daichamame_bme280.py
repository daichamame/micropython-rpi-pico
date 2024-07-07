"""
    BME280
    温度、湿度、気圧取得
    I2C Interface
"""
from machine import Pin, I2C
import time
from ustruct import unpack

class BME280(object):
    # I2C
    I2C_ADDRESS      = const(0x76)
    
    # Address
    ADDR_CALLIBRATION_00 = 0x88
    ADDR_ID              = 0xD0
    ADDR_RESET           = 0xE0
    ADDR_CALLIBRATION_26 = 0xE1
    ADDR_CTRL_HUM        = 0xF2
    ADDR_CTRL_MEAS       = 0xF4
    ADDR_DATA            = 0xF7
    
    def __init__(self,scl_pin=None,sda_pin=None):
        # sclとsdaのいずれかでもNoneならデフォルトピン使用
        if(scl_pin is None or sda_pin is None):
            self.i2c = I2C(0,scl=Pin(5),sda=Pin(4),freq=400000)
        else:
            self.i2c = I2C(0,scl=Pin(scl_pin),sda=Pin(sda_pin),freq=400000)
       
    # 初期化処理（リセットを実行）
    def init(self):
        """ 初期化 """
        self.reset()
        time.sleep_ms(100)
        # OVERSAMPLINGを8（100）で設定       
        # 00000 100
        self.i2c.writeto_mem(self.I2C_ADDRESS,self.ADDR_CTRL_HUM,b'\x04')
        # 100 100 11
        self.i2c.writeto_mem(self.I2C_ADDRESS,self.ADDR_CTRL_MEAS,b'\x93')
        time.sleep_ms(200)

    # id
    def get_id(self):
        """ BME280かBMP280の判定"""
        ret=unpack("<B",self.i2c.readfrom_mem(self.I2C_ADDRESS,self.ADDR_ID, 1))[0]
        if (ret == 0x60):
            return "BME280"
        elif(ret == 0x56 or ret == 0x57 or ret== 0x58):
            return "BMP280"
        return "None"
    # リセット
    def reset(self):
        """ リセット """
        self.i2c.writeto_mem(self.I2C_ADDRESS,self.ADDR_RESET,b'\xB6')
    # データ取得
    def get_data(self):
        """ 温度、湿度、気圧の取得 """
        # キャリブレーション
        dig_00 = self.i2c.readfrom_mem(self.I2C_ADDRESS,self.ADDR_CALLIBRATION_00,26)
        dig_26 = self.i2c.readfrom_mem(self.I2C_ADDRESS,self.ADDR_CALLIBRATION_26,7)
        (dig_T1,dig_T2,dig_T3,dig_P1,dig_P2,dig_P3,dig_P4,dig_P5, \
         dig_P6,dig_P7,dig_P8,dig_P9,dig_H1) = unpack("<HhhHhhhhhhhhB",dig_00)
        (dig_H2,dig_H3,dig_H4,dig_H45,dig_H5,dig_H6) = unpack("<hBbbbb",dig_26) # dig_H4 = 8bit dig_H45 = 8bit dig_H5 = 8bit
      
        dig_H4 = (dig_H4 << 4) + (dig_H45 & 0x0f)              # dig_H4 8bit -> 12bit
        dig_H5 = (dig_H5 << 4) + ((dig_H45 & 0xf0) >> 4)       # dig_H5 8bit -> 12bit
       
        # ローデータ
        rawdata=bytearray(8)
        self.i2c.readfrom_mem_into(self.I2C_ADDRESS,self.ADDR_DATA, rawdata)
        raw_press = (rawdata[0] << 12) | (rawdata[1] << 4) | rawdata[2] >> 4
        raw_temp = (rawdata[3] << 12) | (rawdata[4] << 4) | rawdata[5] >> 4
        raw_hum = (rawdata[6] << 8) | rawdata[7]
        # 気温
        var1 = (((raw_temp >> 3) - (dig_T1 * 2)) * dig_T2) >> 11
        var2 = (raw_temp >> 4) - dig_T1
        var2 = (((var2 * var2) >> 12 ) * dig_T3) >> 14
        t_fine = var1 + var2
        temp = ((t_fine * 5 + 128) >> 8)/100  # ℃
        # 気圧
        var1 = t_fine - 128000
        var2 = var1 * var1 * dig_P6
        var2 = var2 + ((var1 * dig_P5) << 17)
        var2 = var2 + (dig_P4 << 35)
        var1 = (((var1 * var1 * dig_P3) >> 8) +
                ((var1 * dig_P2) << 12))
        var1 = (((1 << 47) + var1) * dig_P1) >> 33
        if var1 == 0:
            pressure = 0
        else:
            p = ((((1048576 - raw_press) << 31) - var2) * 3125) // var1
            var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (dig_P8 * p) >> 19
            pressure = ((((p + var1 + var2) >> 8) + (dig_P7 << 4)) >> 8)/100  # hPa
        # 湿度
        humidity = t_fine - 76800
        humidity = (((((raw_hum << 14) - (dig_H4 << 20) -(dig_H5 * humidity)) + 16384) >> 15) *
             (((((((humidity * dig_H6) >> 10) *(((humidity * dig_H3) >> 11) + 32768)) >> 10) + 2097152) *dig_H2 + 8192) >> 14))
        humidity = humidity - (((((humidity >> 15) * (humidity >> 15)) >> 7) * dig_H1) >> 4)
        
        if humidity < 0:
            humidity = 0
        elif humidity > 419430400:
            humidity = 419430400
        humidity = (humidity >> 12)/1024

        return temp,pressure,humidity





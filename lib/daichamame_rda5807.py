"""
    RDA5807(RDA5807MS)
    I2C Interface
    for Raspberry Pi Pico
"""
from machine import Pin,I2C  
import time

class RDA5807(object):
    # バルク用アドレス 0x10は未使用
    RANDOM_ADDRESS	= 0x11
    def __init__(self, ch=0,scl_pin = 5,sda_pin = 4,frequency=100000):
        self.i2c = I2C(ch,scl=Pin(scl_pin),sda=Pin(sda_pin),freq=frequency)

    # レジスタにデータを描きこむ
    def send_data(self,reg,data):
        """ 指定したレジスタに2バイトのデータを書き込み """
        data_h = data >> 8
        data_l = data & 0xff
        val=bytes([reg])+bytes([data_h])+bytes([data_l])
        self.i2c.writeto(self.RANDOM_ADDRESS, val)

    # レジスタからデータを取得する
    def recv_data(self,reg):
        """ 指定したレジスタから２バイトのデータを取得 """
        recvbuf=bytearray(2)
        self.i2c.writeto(self.RANDOM_ADDRESS,bytes([reg]))
        recvbuf = self.i2c.readfrom(self.RANDOM_ADDRESS, 2)
        return recvbuf

    # 初期設定
    def init(self):
        self.send_data(0x02,0xc001) # DHIZ:Normal DMUTE:Normal Power:Enable
        self.send_data(0x03,0x0000) # tune
        self.send_data(0x04,0x0e00) # De-emphasis:50us softmute:enable
        self.send_data(0x05,0x888b) # volume default
        self.send_data(0x06,0x0000) # i2s default
        self.send_data(0x07,0x4202) # blend default       

    # 選局(03H)
    def set_freq(self,freq):
        """ 周波数は、MHzで指定 """
        if(freq > 76 and freq < 108):
            chan = int((freq - 76)*1000/100)
            data = (chan << 6) + 0x18   # Band:World Wide SPACE:100kHz 
            self.send_data(0x03,data)
    # 現在の選局を取得(05h)
    def get_freq(self):
        """ MHzで取得 """
        buf = self.recv_data(0x03)
        val = (buf[0] << 2) + (buf[1] >> 6)
        return (val+760)/10    
    # ボリュームの設定(05h)
    def set_volume(self,vol):
        """ vol:0 - 15 """
        if(vol >= 0 and vol < 16):
            data=0x8880 + (vol & 0xf)
            self.send_data(0x05,data)
    # ボリュームの取得(05h)
    def get_volume(self):
        """ vol:0 - 15 """
        buf = self.recv_data(0x05)
        return int(buf[1] & 0x0f)

    # ラジオ局判定
    def check_station(self):
        """ 現在のチャネルがラジオ局かどうかレジスタの値から判定 """
        bit = self.recv_data(0x0b)
        return (bit[0] & 0x1) == 1

    # すべてのレジスタ取得(デバッグ用)
    def get_reg(self):
        """ レジスタの値をチェックするため """
        print("reg:fedcba98|76543210")
        for i in range(16):
            buf=self.recv_data(i)
            val= "{:08b}".format(buf[0]) + "|" +  "{:08b}".format(buf[1])
            print(str(hex(i)) + ":" + val)

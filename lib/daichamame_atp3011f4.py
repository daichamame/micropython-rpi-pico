"""
    ATP3011F4
    Text To Talk
    I2C Interface
    コマンド入力モード用(PMOD1/PMOD0=1)
"""
from machine import Pin,I2C
import time

class ATP3011F4(object):
    # I2C
    ADDRESS      = const(0x2e)
    def __init__(self):
        self.i2c = I2C(0,scl=Pin(1),sda=Pin(0),freq=400000)
    # バージョン
    def version(self):
        self.i2c.writeto(self.ADDRESS,"#V\r")
        return self.i2c.readfrom(self.ADDRESS,1)
    # チャイムを鳴らす（ch=0/1)
    def chime(self,ch):
        if(ch==0):
            self.i2c.writeto(self.ADDRESS,"#J\r")
        elif(ch==1):
            self.i2c.writeto(self.ADDRESS,"#K\r")
        self.wait()
        return self.i2c.readfrom(self.ADDRESS,1)
    # 発声終了まで待機
    def wait(self):
        while self.i2c.readfrom(self.ADDRESS,1) == b'*':          
            time.sleep_ms(100)
    # コマンド送信        
    def send_cmd(self, command):
        self.cmd = command + '\r'
        self.i2c.writeto(self.ADDRESS,self.cmd)
        # 発声中は、待機
        self.wait()
        return self.i2c.readfrom(self.ADDRESS,1)
    # 年月日
    def talk_date(self,year,month,day):
        self.send_cmd("'hidukewa <NUMK VAL=" + str(year) + \
                      " COUNTER=nenn> <NUMK VAL=" + str(month) + \
                      " COUNTER=gatu> <NUMK VAL=" + str(day) + \
                      " COUNTER=nichi>de_su.")
    # 時分
    def talk_time(self,hour,minute):
        self.send_cmd("ji'kokuwa <NUMK VAL=" + str(hour) + \
                      " COUNTER=ji> <NUMK VAL=" + str(minute) +\
                      " COUNTER=funn>de_su.")
    # 気温、湿度
    def talk_temp(self,temp,hum):
        self.send_cmd("'kionwa <NUMK VAL=" +str(temp) + \
                      " COUNTER=do>. shi'tudowa <NUMK VAL=" + \
                      str(hum) + " COUNTER=pa-sento>de_su.")
    # 電話番号
    def talk_telno(self,telno):
        self.send_cmd("denwaba'ngo-wa <NUM VAL="+ telno +">de_su.")
    # 金額
    def talk_amount(self,amount):
        self.send_cmd("kingaku-wa <NUMK VAL="+str(amount)+" COUNTER=enn>de_su.")
    # コード
    def talk_code(self,code):
        self.send_cmd("ko-doba'ngo-wa <ALPHA VAL="+ code +">de_su.")

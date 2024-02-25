"""
    AQM1602
    Resolution: 16 x 2 
    I2C Interface
    for Raspberry Pi Pico
"""

from machine import Pin,I2C  
import time

class AQM1602(object):
    # カナ文字変換表
    kana=(
    [0xEFBDA1,0xa1], # ｡
    [0xEFBDA2,0xa2], # ｢
    [0xEFBDA3,0xa3], # ｣
    [0xEFBDA4,0xa4], # ､
    [0xEFBDA5,0xa5], # ･
    [0xEFBDA6,0xa6], # ｦ
    [0xEFBDA7,0xa7], # ｧ
    [0xEFBDA8,0xa8], # ｨ
    [0xEFBDA9,0xa9], # ｩ
    [0xEFBDAA,0xaa], # ｪ
    [0xEFBDAB,0xab], # ｫ
    [0xEFBDAC,0xac], # ｬ
    [0xEFBDAD,0xad], # ｭ
    [0xEFBDAE,0xae], # ｮ
    [0xEFBDAF,0xaf], # ｯ
    [0xEFBDB0,0xb0], # ｰ
    [0xEFBDB1,0xb1], # ｱ
    [0xEFBDB2,0xb2], # ｲ
    [0xEFBDB3,0xb3], # ｳ
    [0xEFBDB4,0xb4], # ｴ
    [0xEFBDB5,0xb5], # ｵ
    [0xEFBDB6,0xb6], # ｶ
    [0xEFBDB7,0xb7], # ｷ
    [0xEFBDB8,0xb8], # ｸ
    [0xEFBDB9,0xb9], # ｹ
    [0xEFBDBA,0xba], # ｺ
    [0xEFBDBB,0xbb], # ｻ
    [0xEFBDBC,0xbc], # ｼ
    [0xEFBDBD,0xbd], # ｽ
    [0xEFBDBE,0xbe], # ｾ
    [0xEFBDBF,0xbf], # ｿ
    [0xEFBE80,0xc0], # ﾀ
    [0xEFBE81,0xc1], # ﾁ
    [0xEFBE82,0xc2], # ﾂ
    [0xEFBE83,0xc3], # ﾃ
    [0xEFBE84,0xc4], # ﾄ
    [0xEFBE85,0xc5], # ﾅ
    [0xEFBE86,0xc6], # ﾆ
    [0xEFBE87,0xc7], # ﾇ
    [0xEFBE88,0xc8], # ﾈ
    [0xEFBE89,0xc9], # ﾉ
    [0xEFBE8A,0xca], # ﾊ
    [0xEFBE8B,0xcb], # ﾋ
    [0xEFBE8C,0xcc], # ﾌ
    [0xEFBE8D,0xcd], # ﾍ
    [0xEFBE8E,0xce], # ﾎ
    [0xEFBE8F,0xcf], # ﾏ
    [0xEFBE90,0xd0], # ﾐ
    [0xEFBE91,0xd1], # ﾑ
    [0xEFBE92,0xd2], # ﾒ
    [0xEFBE93,0xd3], # ﾓ
    [0xEFBE94,0xd4], # ﾔ
    [0xEFBE95,0xd5], # ﾕ
    [0xEFBE96,0xd6], # ﾖ
    [0xEFBE97,0xd7], # ﾗ
    [0xEFBE98,0xd8], # ﾘ
    [0xEFBE99,0xd9], # ﾙ
    [0xEFBE9A,0xda], # ﾚ
    [0xEFBE9B,0xdb], # ﾛ
    [0xEFBE9C,0xdc], # ﾜ
    [0xEFBE9D,0xdd], # ﾝ
    [0xEFBE9E,0xde], # ﾞ
    [0xEFBE9F,0xdf] # ﾟ
    )

    # I2C
    ADDRESS      = const(0x3e)
    def __init__(self):
        self.i2c = I2C(0,scl=Pin(1),sda=Pin(0),freq=400000)
        self.cmd = bytearray(2)
    def init(self):
        time.sleep_ms(40)
        self.send_cmd(0x38) # Function Set 
        self.send_cmd(0x39) # Function Set IS = 1
        self.send_cmd(0x14) # Internal OSC frequency
        self.send_cmd(0x76) # Contrast Set
        self.send_cmd(0x56) # Power / ICON /Contrast Control
        self.send_cmd(0x6C) # Follower control
        time.sleep_ms(200)
        self.send_cmd(0x38) # Function Set IS = 0
        self.send_cmd(0x0C) # Display On
        self.send_cmd(0x01) # Clear Display
        self.send_cmd(0x07) # Entry mode
        time.sleep_ms(1)        
    # コマンドを送信する
    def send_cmd(self, command):
        self.cmd[0] = 0x00
        self.cmd[1] = command
        self.i2c.writeto(self.ADDRESS,self.cmd)
    # データを送信する
    def send_data(self, buf):
        self.i2c.writeto(self.ADDRESS,b'\x40'+buf) 
    # 挨拶
    def hello(self):
        self.print(1,"ｺﾝﾆﾁﾊ")
        self.print(2,"  AQM1602")
    # クリア
    def clear(self):
        self.send_cmd(0x01)
    # コード取得
    def get_cgram_addr(self,code):
        """ 文字コードからCGRAMアドレスを取得 """
        l_num = 0
        h_num = len(self.kana)-1
        while(l_num <= h_num): # 二分探索を使って、
            m_num = int((h_num+l_num)/2)
            if(int(code) == self.kana[m_num][0]):
                return self.kana[m_num][1]
            elif(int(code) < self.kana[m_num][0]):
                h_num = m_num-1
            else:
                l_num = m_num+1
        return 0x20   # 見つからなかった場合
    # 表示
    def print(self,line,buf):
        """ line:1 or 2 buf:表示文字列 """
        # Set DDRAM address
        if(line == 1):  # １行目
            self.send_cmd(0x80)
        elif(line == 2):# ２行目
            self.send_cmd(0xc0)
        else:           # それ以外は1行目
            self.send_cmd(0x80)            
        time.sleep_ms(10)
        for i in buf:
            if(ord(i) <= 0x7f): #ASCII
                self.send_data(i.encode())
            else: # 0x80以降
                kn = self.get_cgram_addr("0x"+i.encode('utf-8').hex())
                self.send_data( kn.to_bytes(1,'little'))
        

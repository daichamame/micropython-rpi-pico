"""
    OLED(SSD1306)
    Resolution: 128 x 64 dot matrix panel 
    I2C Interface
    for Raspberry Pi Pico
"""
from machine import Pin,I2C  
import time
import framebuf

class SSD1306(object):
    # 色
    WHITE   = const(1)
    BLACK   = const(0)
    # 画像解像度
    WIDTH        = const(128)
    HEIGHT       = const(64)
    PAGE_NUM     = const(8)
    BUFFER_SIZE  = WIDTH * PAGE_NUM
    # I2C
    ADDRESS      = const(0x3c)
    def __init__(self, rotate,font_array,font_size):
        """ 初期設定 rotate:(0 90 180 270)
        font_array:フォントビットマップ情報
        font_size:フォントサイズ、半角は半分 """
        self.i2c = I2C(0,scl=Pin(1),sda=Pin(0),freq=400000)
        self.rotate = rotate
        self.cmd = bytearray(2)
        self.buffer = bytearray(self.BUFFER_SIZE)
        self.framebuf = framebuf.FrameBuffer(self.buffer,self.WIDTH,self.HEIGHT,framebuf.MONO_VLSB)
        self.col_addr_start = 0
        self.col_addr_end   = self.WIDTH-1
        self.page_addr_start = 0
        self.page_addr_end   = self.PAGE_NUM - 1
        self.font_size = font_size
        self.font_array = font_array
    # OLED初期化
    def init(self):
        """ OLED SSD1306を初期化する """
        self.send_cmd(0xA8) # set mux ratio    a8h,3fh
        self.send_cmd(self.HEIGHT - 1) 
        self.send_cmd(0xD3) # set display offset d3h,00h
        self.send_cmd(0x00)
        self.send_cmd(0x40) # set display start line 40h 
        self.send_cmd(0xA1) # set segment re-map a0h/a1h
        self.send_cmd(0xC8) # set com output scan direction c0h/c8h
        self.send_cmd(0xDA) # set com pins hardware configuration dah,12
        self.send_cmd(0x12)
        self.send_cmd(0x81) # set contrast control 81h,7fh
        self.send_cmd(0x7f)
        self.send_cmd(0xA4) # disable entire display on a4h
        self.send_cmd(0xA6) # set normal display a6h 
        self.send_cmd(0xD5) # set osc frequency d5h,80h
        self.send_cmd(0x80)
        self.send_cmd(0x8D) # set enable charge pump regulator 8dh,14h
        self.send_cmd(0x14)
        self.send_cmd(0xAF) # set display normal
        self.send_cmd(0x20) # set memory address mode
        self.send_cmd(0x00) # horizontal addressing mode
        self.send_cmd(0x2E) # SSD1306_SET_DEACTIVE_SCROLL
    # フラッシュ
    def flash(self):
        """ 画面を点滅する """
        for i in range(2):
            self.send_cmd(0xA5)
            time.sleep_ms(200)
            self.send_cmd(0xA4)
            time.sleep_ms(200)
    # コマンドを送信する
    def send_cmd(self, command):
        self.cmd[0] = 0x80
        self.cmd[1] = command
        self.i2c.writeto(self.ADDRESS,self.cmd)
    # データを送信する
    def send_data(self, buf):
        self.i2c.writeto(self.ADDRESS,b'\x40'+buf)
    # 画面消去/バッファの初期化
    def clear(self):
        """ 画面を消去する"""
        self.framebuf.fill(0)
        self.display()
    # 画面表示
    def display(self):
        """ 表示用配列を利用して画面を表示する"""
        self.send_cmd(0x21) # set col address
        self.send_cmd(self.col_addr_start)
        self.send_cmd(self.col_addr_end)
        self.send_cmd(0x22) # set page address
        self.send_cmd(self.page_addr_start)
        self.send_cmd(self.page_addr_end)
        self.send_data(self.buffer)
        time.sleep_ms(200)
    # 画面の回転を設定
    def set_rotate(self,rotate):
        """ 表示画面を回転させる（rotate=、0 , 90 , 180, 270） """
        if rotate == 0 or rotate == 90 or rotate == 180 or rotate == 270:
            self.rotate = rotate
    # 点を打つ
    def pset(self,px, py, color):
        """ 座標(px,py) に color(白、黒) で指定した色で点を打つ """
        if self.rotate == 0:
            if (px<self.WIDTH)*(py<self.HEIGHT):
                self.framebuf.pixel(px,py,color)         
        elif self.rotate == 90:
            if (px<self.HEIGHT)*(py<self.WIDTH):
                self.framebuf.pixel(py,self.HEIGHT-px,color)
        elif self.rotate == 180:
            if (px<self.WIDTH)*(py<self.HEIGHT):
                self.framebuf.pixel(self.WIDTH-px,self.HEIGHT-py,color)            
        elif self.rotate == 270:
            if (px<self.HEIGHT)*(py<self.WIDTH):
                self.framebuf.pixel(self.WIDTH-py,px,color)            
        else:
            return
    # 大きな点を打つ
    def mpset(self,px,py,color,ratio):
        """ ratioで指定した倍率で点を打つ """
        for i in range(ratio):
            for j in range(ratio):
                self.pset(px + i, py + j,  color)
    # 表示文字のビットマップ情報を取得
    def get_fontdata(self,code):
        """ フォントのビットマップ情報をリストから取得する """
        l_num = 0
        h_num = len(self.font_array)-1
        while(l_num <= h_num): # 二分探索を使用
            m_num = int((h_num+l_num)/2)
            if(int(code) == self.font_array[m_num][0]):
                return self.font_array[m_num]
            elif(int(code) < self.font_array[m_num][0]):
                h_num = m_num-1
            else:
                l_num = m_num+1
        return self.font_array[0]   # フォントが見つからなかった場合
    # 文字を書く
    def print( self,dx, dy, buf,ratio):
        """ 開始位置(dx,dy）からbufの文字列を書く、ratioは、拡大率
        画面に表示する場合には、display()を実行する """
        # 縦横の向きに合わせて幅サイズを調整
        if self.rotate == 0 or self.rotate == 180:
            wx=self.WIDTH
        else:
            wx=self.HEIGHT
        for ch in buf:
            font_data=self.get_fontdata("0x"+ch.encode('utf-8').hex())  # フォントデータを取得
            if ord(ch) < 0x7F: # ASCIIコードの場合
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size/2*ratio)): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size/2):
                        if(int(font_data[j+1])) & (0x80 >> int(i%(self.font_size/2))):
                            self.mpset(dx+i*ratio,dy+j*ratio,self.WHITE,ratio)
                        else:
                            self.mpset(dx+i*ratio,dy+j*ratio,self.BLACK,ratio)
                dx+=int(self.font_size/2*ratio)
            else:   # 日本語の場合
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size*ratio)): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size):
                        if(int(font_data[j+1])) & (0x8000 >> int(i%(self.font_size))):
                            self.mpset(dx+i*ratio,dy+j*ratio,self.WHITE,ratio)
                        else:
                            self.mpset(dx+i*ratio,dy+j*ratio,self.BLACK,ratio)
                dx+=int(self.font_size*ratio)
    # 線をひく
    def line(self,sx,sy,ex,ey):
        """開始位置(sx,sy)から、終了位置(ex,ey)まで直線を描く 画面に表示する場合には、display()を実行する"""
        if self.rotate == 0:
            self.framebuf.line(sx,sy,ex,ey,self.WHITE)
        elif self.rotate == 90:
            self.framebuf.line(sy,self.HEIGHT-sx,ey,self.HEIGHT-ex,self.WHITE)
        elif self.rotate == 180:
            self.framebuf.line(self.WIDTH-sx,self.HEIGHT-sy,self.WIDTH-ex,self.HEIGHT-ey,self.WHITE)
        elif self.rotate == 270:
            self.framebuf.line(self.WIDTH-sy,sx,self.WIDTH-ey,ex,self.WHITE)
        else:
            return

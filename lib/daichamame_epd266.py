"""
    waveshare 2.66inch E-Paper E-Ink Display Module
    Resolution: 292 x 152 dot matrix panel 
    SPI Interface
    for Raspberry Pi Pico
"""
from machine import Pin,SPI  
import time
import framebuf

class Epd266(object):
    # 表示色
    WHITE   = const(0xFF)
    BLACK   = const(0x00)
    # 解像度
    WIDTH        = const(152)
    HEIGHT       = const(296)
    WIDTH_BYTE   = int(WIDTH/8)
    BUFFER_SIZE  = WIDTH_BYTE * HEIGHT
    WF_PARTIAL = bytes([
        0x00,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x80,0x80,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x40,0x40,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x80,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x01,0x00,0x00,
        0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0x00,0x00,0x00,0x00,0x22,0x22,0x22,0x22,0x22,0x22,
        0x00,0x00,0x00,0x22,0x17,0x41,0xB0,0x32,0x36,
    ])
    # 使用GPIO
    RST_PIN     = 12
    DC_PIN      = 8
    CS_PIN      = 9
    BUSY_PIN    = 13
    CLK_PIN     = 10
    MOSI_PIN    = 11

    def __init__(self, rotate,font_array,font_size):
        """ 初期設定 rotate:(0 90 180 270)
        font_array:フォントビットマップ情報
        font_size:フォントサイズ、半角は半分 """
        self.spi = SPI(1)
        self.rate = 4 * 1000 * 1000 # 4MHz
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs     = Pin(self.CS_PIN)
        self.dc     = Pin(self.DC_PIN)
        self.rst    = Pin(self.RST_PIN)
        self.busy   = Pin(self.BUSY_PIN)
        self.clk    = Pin(self.CLK_PIN)
        self.mosi   = Pin(self.MOSI_PIN)
        self.width  = self.WIDTH
        self.height = self.HEIGHT
        self.rotate = rotate
        self.buffer = bytearray(self.BUFFER_SIZE)
        self.framebuf = framebuf.FrameBuffer(self.buffer,self.WIDTH,self.HEIGHT,framebuf.MONO_HLSB)
        self.font_array = font_array
        self.font_size = font_size
        
    # 電子ペーパー初期化
    def init(self):
        """ 電子ペーパーを初期化する 
        display()を実行するごとに反転表示を行う
        """
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.cs.init(self.cs.OUT, value=1)
        self.busy.init(self.busy.IN)
        self.reset()
        self.read_busy()
        self.send_cmd(0x12)
        self.read_busy()
        self.send_cmd(0x11)
        self.send_data(0x03)
        self.send_cmd(0x44)
        self.send_data(0x01) 
        self.send_data(0x13)
        self.send_cmd(0x45)
        self.send_data(0)
        self.send_data(0)
        self.send_data(0x27)
        self.send_data(0x01)
        self.read_busy()
    # 電子ペーパー初期化（パーシャル）
    def init_partial(self):
        """ 電子ペーパーを初期化する 
        display()を実行した際に反転表示が行われない
        消した文字が残ってしまうことがある場合は、
        init()+clear()を使う
        """
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.cs.init(self.cs.OUT, value=1)
        self.busy.init(self.busy.IN)
        self.reset()
        self.read_busy()
        self.send_cmd(0x12)
        self.read_busy()
        self.set_LUA()
        self.send_cmd(0x37) 
        self.send_data(0x00)  
        self.send_data(0x00)  
        self.send_data(0x00)  
        self.send_data(0x00) 
        self.send_data(0x00)
        self.send_data(0x40)  
        self.send_data(0x00)  
        self.send_data(0x00)   
        self.send_data(0x00)  
        self.send_data(0x00)
        self.send_cmd(0x11)
        self.send_data(0x03)
        self.send_cmd(0x44)
        self.send_data(0x01) 
        self.send_data(0x13)
        self.send_cmd(0x45)
        self.send_data(0)
        self.send_data(0)
        self.send_data(0x27)
        self.send_data(0x01)
        self.send_cmd(0x3C) 
        self.send_data(0x80)   
        self.send_cmd(0x22) 
        self.send_data(0xcf) 
        self.send_cmd(0x20) 
        self.read_busy()
    # リセット
    def reset(self):
        self.rst(1)
        time.sleep_ms(200)
        self.rst(0)
        time.sleep_ms(2)
        self.rst(1)
        time.sleep_ms(200)
    # コマンドを送信する
    def send_cmd(self, command):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytes([command]))
        self.cs(1)
    # データを送信する
    def send_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytes([buf]))
        self.cs(1)
    # busy を確認してアイドリング
    def read_busy(self):
        time.sleep_ms(100)
        while(self.busy == 1): # LOW: idle, HIGH: busy
            time.sleep_ms(100)
        time.sleep_ms(100)
    # LUA の設定
    def set_LUA(self):
        self.send_cmd(0x32)
        for i in self.WF_PARTIAL:
            self.send_data(i)
        self.read_busy()
    # 画面消去
    def clear(self):
        """ 画面一面を白で埋める"""
        self.send_cmd(0x24)
        for i in range(self.BUFFER_SIZE):
            self.send_data(self.WHITE)    #      白で描画
        self.send_cmd(0x20)
        self.read_busy()
        self.display()
    # 待機
    def sleep(self):
        self.send_cmd(0x10)
        self.read_busy()
    # 画面表示
    def display(self):
        """ 表示用配列を利用して画面を表示する"""
        self.send_cmd(0x24)
        for i in range(self.BUFFER_SIZE):
            self.send_data(self.buffer[i])
        self.send_cmd(0x20)
        self.read_busy()
        time.sleep_ms(500)
    # バッファの初期化
    def buffer_clear(self):
        """ 表示用配列を初期化する """
        self.framebuf.fill(1)
    # 画面の回転を設定
    def set_rotate(self,rotate):
        """ 表示画面を回転させる（rotate=、0 , 90 , 180, 270） """
        if rotate == 0 or rotate == 90 or rotate == 180 or rotate == 270:
            self.rotate = rotate
    # 点を打つ
    def pset(self,px, py, color):
        """ 座標(px,py) に color(白、黒) で指定した色で点を打つ  """
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
        for i in range(ratio):
            for j in range(ratio):
                self.pset(px + i, py + j,  color)
    # 表示文字のビットマップ情報を取得
    def get_fontdata(self,code):
        """ フォントのビットマップ情報をリストから取得する """
        l_num = 0
        h_num = len(self.font_array)-1

        while(l_num <= h_num): # 二分探索を使って、
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
            self.fontdata=self.get_fontdata("0x"+ch.encode('utf-8').hex())  # フォントデータを取得
            if ord(ch) < 0x7F: # ASCIIコードの場合(8x16)
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size/2*ratio)): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size/2):
                        if(int(self.fontdata[j+1])) & (0x80 >> int(i%(self.font_size/2))):
                            self.mpset(dx+i*ratio,dy+j*ratio,self.BLACK,ratio)
                        else:
                            self.mpset(dx+i*ratio,dy+j*ratio,self.WHITE,ratio)
                dx+=int(self.font_size/2*ratio)
            else:   # 日本語の場合(16x16)
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size*ratio)): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size):
                        if(int(self.fontdata[j+1])) & (0x8000 >> int(i%(self.font_size))):
                            self.mpset(dx+i*ratio,dy+j*ratio,self.BLACK,ratio)
                        else:
                            self.mpset(dx+i*ratio,dy+j*ratio,self.WHITE,ratio)
                dx+=int(self.font_size*ratio)
    # 線をひく
    def line(self,sx,sy,ex,ey):
        """開始位置(sx,sy)から、終了位置(ex,ey)まで直線を描く 画面に表示する場合には、display()を実行する"""
        if self.rotate == 0:
            self.framebuf.line(sx,sy,ex,ey,self.BLACK)
        elif self.rotate == 90:
            self.framebuf.line(sy,self.HEIGHT-sx,ey,self.HEIGHT-ex,self.BLACK)
        elif self.rotate == 180:
            self.framebuf.line(self.WIDTH-sx,self.HEIGHT-sy,self.WIDTH-ex,self.HEIGHT-ey,self.BLACK)
        elif self.rotate == 270:
            self.framebuf.line(self.WIDTH-sy,sx,self.WIDTH-ey,ex,self.BLACK)
        else:
            return
    # アイコン(32x32)を描く
    def draw_icon(self,dx, dy, buf,ratio):
        """ 開始位置(dx,dy）からbufのアイコンデータを描く、ratioは、拡大率
        画面に表示する場合には、display()を実行する """
        for j in range(64):
            for i in range(16):
                if(int(buf[j])) & (0x8000 >> int(i%16)):
                    self.mpset(dx+i*ratio+16*(j%2==1)*ratio,dy+int(j/2)*ratio,self.BLACK,ratio)
                else:
                    self.mpset(dx+i*ratio+16*(j%2==1)*ratio,dy+int(j/2)*ratio,self.WHITE,ratio)
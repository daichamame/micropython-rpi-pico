"""
    waveshare 2.66inch E-Paper E-Ink Display Module
    Resolution: 292 x 152 dot matrix panel 
    SPI Interface
    for Raspberry Pi Pico
"""
from machine import Pin,SPI  
import time
import framebuf

try:# フォント関連のモジュールのインポート(拡張予定)
    import daichamame_util
except ImportError:
    print("No module named 'daichamame_util'")

class Epd266(object):
    # 表示色(区別するためのもの)
    WHITE   = const(0xFF)
    BLACK   = const(0x00)
    RED     = const(0xE0)
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
        self.width  = self.WIDTH
        self.height = self.HEIGHT
        self.rotate = rotate
        self.buffer_black = bytearray(self.BUFFER_SIZE) # 白黒用バッファ
        self.buffer_red = bytearray(self.BUFFER_SIZE)   # 赤用バッファ
        self.framebuf_black = framebuf.FrameBuffer(self.buffer_black,self.WIDTH,self.HEIGHT,framebuf.MONO_HLSB)
        self.framebuf_red = framebuf.FrameBuffer(self.buffer_red,self.WIDTH,self.HEIGHT,framebuf.MONO_HLSB)
        self.font_array = font_array
        self.font_size = font_size
        if font_array == None: # font_arrayが空の場合フォントライブラリをimportする
            try:
                self.util=daichamame_util.util(font_size)
            except:
                print("The module 'daichamame_util' is unavailable.")
        self.init()

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
    # 画面データを送信する
    def send_image_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray(buf))
        self.cs(1)
    # busy を確認してアイドリング
    def read_busy(self):
        while(self.busy.value() == 1): # LOW: idle, HIGH: busy
            time.sleep_ms(10)
    # LUA の設定
    def set_LUA(self):
        self.send_cmd(0x32)
        for i in self.WF_PARTIAL:
            self.send_data(i)
        self.read_busy()
    # 画面消去
    def clear(self,color=WHITE):
        """ 画面一面を白で埋める"""
        self.send_cmd(0x24) # 白黒
        self.send_image_data([color] * self.BUFFER_SIZE)
        self.send_cmd(0x26) # 赤
        self.send_image_data([0x00] * self.BUFFER_SIZE)
        self.send_cmd(0x20)
        self.update_display()
    # 待機
    def sleep(self):
        self.send_cmd(0x10)
        self.read_busy()
    # 画面表示
    def display(self):
        """ 表示用配列を利用して画面を表示する"""
        self.send_cmd(0x24) # 白黒
        self.send_image_data(self.buffer_black)
        self.send_cmd(0x26) # 赤
        self.send_image_data(self.buffer_red)
        self.send_cmd(0x20)
        self.update_display()
    # 
    def update_display(self):
        """ DISPLAY MODEは1 """
        self.send_cmd(0x22)
        self.send_data(0xcf)
        self.send_cmd(0x20)
        self.read_busy()

    # バッファの初期化
    def buffer_clear(self):
        """ 表示用配列を初期化する """
        self.framebuf_black.fill(1)
        self.framebuf_red.fill(0)

    # 画面の回転を設定
    def set_rotate(self,rotate):
        """ 表示画面を回転させる（rotate=、0 , 90 , 180, 270） """
        if rotate == 0 or rotate == 90 or rotate == 180 or rotate == 270:
            self.rotate = rotate
    # 点を打つ
    def pset(self,px, py, color):
        """ 座標(px,py) に color(白、黒、赤) で指定した色で点を打つ  """
        if self.rotate == 0:
            if (px<self.WIDTH)*(py<self.HEIGHT):
                if color == self.RED:
                    self.framebuf_red.pixel(px,py,0x1)
                else:
                    self.framebuf_black.pixel(px,py,color)         
        elif self.rotate == 90:
            if (px<self.HEIGHT)*(py<self.WIDTH):
                if color == self.RED:
                    self.framebuf_red.pixel(py,self.HEIGHT-px,0x1)
                else:
                    self.framebuf_black.pixel(py,self.HEIGHT-px,color)
        elif self.rotate == 180:
            if (px<self.WIDTH)*(py<self.HEIGHT):
                if color == self.RED:
                    self.framebuf_red.pixel(self.WIDTH-px,self.HEIGHT-py,0x1)
                else:
                    self.framebuf_black.pixel(self.WIDTH-px,self.HEIGHT-py,color)            
        elif self.rotate == 270:
            if (px<self.HEIGHT)*(py<self.WIDTH):
                if color == self.RED:
                    self.framebuf_red.pixel(self.WIDTH-py,px,0x1)
                else:
                    self.framebuf_black.pixel(self.WIDTH-py,px,color)            
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
        icode= int.from_bytes(code, 'big')
        l_num = 0
        h_num = len(self.font_array)-1

        while(l_num <= h_num): # 二分探索を使って、
            m_num = int((h_num+l_num)/2)
            if(icode == self.font_array[m_num][0]):
                return self.font_array[m_num][1:17]
            elif(icode < self.font_array[m_num][0]):
                h_num = m_num-1
            else:
                l_num = m_num+1
        return self.font_array[0][1:17]   # フォントが見つからなかった場合
    # 文字を書く
    def print( self,dx, dy, buf,ratio=1,color=BLACK,invert=False):
        """ 開始位置(dx,dy）
        buf:表示文字列
        ratio:拡大率(1,2,3..)
        color:フォントの色(既定値 黒)
        invert:反転（既定値 False)
        画面に表示する場合には、display()を実行する """
        # 文字色と背景色の設定
        if invert is False:
            font_color = color
            background_color = self.WHITE
        else:
            font_color = self.WHITE
            background_color = color
        # 縦横の向きに合わせて幅サイズを調整
        if self.rotate == 0 or self.rotate == 180:
            wx=self.WIDTH
        else:
            wx=self.HEIGHT
        # 文字数分繰り返す
        for ch in buf:
            if self.font_array is None:
                try:
                    fontdata=self.util.get_fontdata(ch.encode('utf-8'))  # フォントデータを取得
                except:
                    fontdata=[0x00]*self.font_size # フォントデータを取得
            else:
                fontdata=self.get_fontdata(ch.encode('utf-8'))  # フォントデータを取得                
            utf8code = int.from_bytes(ch.encode('utf-8'), 'big')
            # ASCIIコードまたは半角カタカナの場合
            if utf8code < 0x7F or (utf8code >= 0xEFBDA1 and utf8code <= 0xEFBDBF) or (utf8code >= 0xEFBE80 and utf8code <= 0xEFBE9F): 
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size/2*ratio)): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size/2):
                        if(int(fontdata[j])) & (0x80 >> int(i%(self.font_size/2))):
                            self.mpset(dx+i*ratio,dy+j*ratio,font_color,ratio)
                        else:
                            self.mpset(dx+i*ratio,dy+j*ratio,background_color,ratio)
                dx+=int(self.font_size/2*ratio)
            else:   # 日本語の場合(16x16)
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size*ratio)): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size):
                        if(int(fontdata[j])) & (0x8000 >> int(i%(self.font_size))):
                            self.mpset(dx+i*ratio,dy+j*ratio,font_color,ratio)
                        else:
                            self.mpset(dx+i*ratio,dy+j*ratio,background_color,ratio)
                dx+=int(self.font_size*ratio)
    # 線をひく
    def line(self,sx,sy,ex,ey):
        """開始位置(sx,sy)から、終了位置(ex,ey)まで直線を描く 画面に表示する場合には、display()を実行する"""
        if self.rotate == 0:
            self.framebuf_black.line(sx,sy,ex,ey,self.BLACK)
        elif self.rotate == 90:
            self.framebuf_black.line(sy,self.HEIGHT-sx,ey,self.HEIGHT-ex,self.BLACK)
        elif self.rotate == 180:
            self.framebuf_black.line(self.WIDTH-sx,self.HEIGHT-sy,self.WIDTH-ex,self.HEIGHT-ey,self.BLACK)
        elif self.rotate == 270:
            self.framebuf_black.line(self.WIDTH-sy,sx,self.WIDTH-ey,ex,self.BLACK)
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


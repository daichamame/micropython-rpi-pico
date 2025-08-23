"""
   Pico LCD 1.3

   LCD:ST7789VW
   表示:240x240 RGB（メモリは240x320)
   ジョイスティックと4つのボタン
   
   描画に関して、文字やアイコンで一部Framebufを使用しているが、
   線、四角形、ビットマップ画像は直接書き込んでいる
   色の指定は、rgbそれぞれ1バイトで、0xffffffのように24ビットの形式
   
"""
from machine import Pin,SPI  
import time
import framebuf
import micropython
import gc

try:# フォント関連のモジュールのインポート(存在していれば)
    import daichamame_util
except ImportError:
    print("No module named 'daichamame_util'")

class PICOLCD13(object):
    # GPIO
    KEY_A       = 15
    KEY_B       = 17
    KEY_X       = 19
    KEY_Y       = 21
    JOY_U       = 2
    JOY_D       = 18
    JOY_L       = 16
    JOY_R       = 20
    JOY_C       = 3
    RST_PIN     = 12
    DC_PIN      = 8
    CS_PIN      = 9
    BUSY_PIN    = 13
    CLK_PIN     = 10
    DIN_PIN     = 11

    # 画面表示のサイズ（240 x 320　のうち一部のみ表示されている） 
    SCREEN_WIDTH  = 240
    SCREEN_HEIGHT = 240
    def __init__(self, font_array,font_size,rotate=0):
        self.spi = SPI(1)
        self.rate = 4 * 1000 * 1000 # 4MHz
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs     = Pin(self.CS_PIN)
        self.dc     = Pin(self.DC_PIN)
        self.rst    = Pin(self.RST_PIN)
        self.busy   = Pin(self.BUSY_PIN)
        self.din    = Pin(self.DIN_PIN)
        self.clk    = Pin(self.CLK_PIN)

        # ジョイスティックとボタンを定義
        self.key_a  = Pin(self.KEY_A,Pin.IN,Pin.PULL_UP)
        self.key_b  = Pin(self.KEY_B,Pin.IN,Pin.PULL_UP)
        self.key_x  = Pin(self.KEY_X,Pin.IN,Pin.PULL_UP)
        self.key_y  = Pin(self.KEY_Y,Pin.IN,Pin.PULL_UP)
        self.joy_u  = Pin(self.JOY_U,Pin.IN,Pin.PULL_UP)
        self.joy_d  = Pin(self.JOY_D,Pin.IN,Pin.PULL_UP)
        self.joy_l  = Pin(self.JOY_L,Pin.IN,Pin.PULL_UP)
        self.joy_r  = Pin(self.JOY_R,Pin.IN,Pin.PULL_UP)
        self.joy_c  = Pin(self.JOY_C,Pin.IN,Pin.PULL_UP)

        # 90度回転とそれ以外の設定 
        self.rotate = rotate
        if self.rotate == 90: # ジョイスティックを左、ボタンを右にした向き
            self.madctl = 0x60
            self.width  = 320
            self.height = 240
        else: # ジョイスティック側を上で、ボタンを下にした向き
            self.madctl = 0x00
            self.width  = 240
            self.height = 320
        self.font_array = font_array
        self.font_size = font_size
        if font_array == None: # 機能拡張用:font_arrayが空の場合フォントライブラリをimportする
            try:
                self.util=daichamame_util.util(font_size)
            except:
                print("The module 'daichamame_util' is unavailable.")
        self.init()
    
    # 初期処理
    def init(self):
        """
        ディスプレイの初期化
        """
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.cs.init(self.cs.OUT, value=1)
        self.busy.init(self.busy.IN)
        self.reset()
        self._set_window(0,0,self.width,self.height)
        self.send_cmd(0x36)     # MADCTL
        self.send_data(self.madctl)
        self.send_cmd(0x3A)     # pixel format
        self.send_data(0x05)    # 16bit mode
        self.send_cmd(0xB0)     # Ram control
        self.send_data(0x00)
        self.send_data(0xF8) # リトルエンディアンに設定        
        self.send_cmd(0xBB)     # VCOM Setting
        self.send_data(0x19)
        self.send_cmd(0xC3)     #  VRH Set 
        self.send_data(0x12)
        self.send_cmd(0x21)     # inversion on 背景を黒に設定
        self.send_cmd(0x11)     # Sleep Out
        self.send_cmd(0x29)     # Display on

    # HWリセット
    def reset(self):
        self.rst(1)
        time.sleep_ms(100)
        self.rst(0)
        time.sleep_ms(100)
        self.rst(1)
        time.sleep_ms(100)
    # SWリセット
    def sw_reset(self):
        self.send_cmd(0x01)
        time.sleep_ms(120)
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
    # イメージデータを送信する
    def send_image_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray(buf))
        self.cs(1)
    # sleep in
    def sleep_in(self):
        self.send_cmd(0x10)
    # sleep out
    def sleep_in(self):
        self.send_cmd(0x11)

    # 描画エリア指定
    def _set_window(self,start_x,start_y,end_x,end_y):
        """
        データを書き込む為のエリアを指定する直接呼び出す必要はない
        """
        self.send_cmd(0x2A)
        self.send_data(((start_x) >> 8) & 0xFF)
        self.send_data(start_x & 0xFF)
        self.send_data(((end_x -1) >> 8) & 0xFF)
        self.send_data(end_x-1 & 0xFF)
        self.send_cmd(0x2B)
        self.send_data(((start_y) >> 8) & 0xFF)
        self.send_data((start_y) & 0xFF)
        self.send_data(((end_y -1) >> 8) & 0xFF)
        self.send_data((end_y-1) & 0xFF)
        self.send_cmd(0x2C)

    # スクロールエリア定義
    def set_scroll(self,tfa,vsa,bfa):
        """
        Top Fixed Area,Vertical Scrolling Area,Bottom Fixed Area 
        3分割で指定する
        320ピクセルまでをスクロールして使用する場合には、
        Vertical Scrolling Areaを320まで指定する
        """
        self.send_cmd(0x33)
        self.send_data(0x00)
        self.send_data(tfa & 0xff)
        self.send_data(0x00)
        self.send_data(vsa & 0xff)
        self.send_data(0x00)
        self.send_data(bfa & 0xff)
    # スクロール
    def scroll(self,num):
        """
        numピクセルの位置に移動
        numの数を増やしていくとスクロールする
        """
        self.send_cmd(0x37)
        self.send_data((num >> 8) & 0xff)
        self.send_data(num & 0xff)

    # RGB 24bit -> RGB 565
    def color565(self,color24):
        """
        color24 : 0xffffff rgbの順に24ビットの形式
        ビットシフトした簡易的な変換
        r : 赤を 8bit -> 5bit
        g : 緑を 8bit -> 6bit
        b : 青を 8bit -> 5bit
        rgbの順に並べて16bitに変換し
        """
        r = (color24 >> 16) & 0xFF
        g = (color24 >>  8) & 0xFF
        b = (color24 & 0xFF)
        return (r >> 3) << 3 | (g >> 5) , ((g << 3) & 0xE0)| (b >> 3)
    # 画面消去
    def clear(self,color=0x000000):
        """
        指定色で塗りつぶす
        色を指定しない場合には、黒で塗りつぶす
        """
        (h_color,l_color) = self.color565(color) # 24bit->16bit
        self._set_window(0,0,self.width,self.height)
        self.dc(1)
        self.cs(0)
        for i in range(self.height):
            self.spi.write(bytearray([l_color,h_color]*self.width))
        self.cs(1)
        self.display_on()
        gc.collect()
    # display off
    def display_off(self):
        self.send_cmd(0x28)
    # display on
    def display_on(self):
        self.send_cmd(0x29)
    # ノーマルモードに設定
    def normal_mode(self):
        self.send_cmd(0x13)
    # 点を打つ
    def pset(self,x,y,color):
        """
        1pixelずつ処理するため、多くの点を処理するときは遅くなる
        """
        (h_color,l_color) = self.color565(color) # 24bit->16bit
        self._set_window(x,y,x+1,y+1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([l_color,h_color]))
        self.cs(1)

    # 表示文字のビットマップ情報を取得
    def _get_fontdata(self,code):
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
    def print( self,dx, dy, buf,color,bgcolor=0x000000,ratio=2,bold=0):
        """ 開始位置(dx,dy）
        buf:表示文字列
        color:フォントの色
        bgcolor:背景色（既定値 0x000000)
        ratio:拡大率(1,2,3)
        bold:太字（0,1,2,3)
        1.3インチに対して縦横240ピクセルの為、2倍の大きさを既定値とした
        """
        wx=self.SCREEN_WIDTH
        (h_color,l_color)=self.color565(color)
        color=(h_color << 8) | l_color
        (h_color,l_color)=self.color565(bgcolor)
        bgcolor=(h_color << 8) | l_color

        # 文字数分繰り返す
        for ch in buf:
            if self.font_array is None:
                try:
                    fontdata=self.util.get_fontdata(ch.encode('utf-8'))  # フォントデータを取得
                except:
                    fontdata=[0x00]*self.font_size # フォントデータを取得
            else:
                fontdata=self._get_fontdata(ch.encode('utf-8'))  # フォントデータを取得                
            utf8code = int.from_bytes(ch.encode('utf-8'), 'big')
            # ASCIIコードまたは半角カタカナの場合
            if utf8code < 0x7F or (utf8code >= 0xEFBDA1 and utf8code <= 0xEFBDBF) or (utf8code >= 0xEFBE80 and utf8code <= 0xEFBE9F): 
                buffer = bytearray((self.font_size+bold*2)*self.font_size*ratio*ratio)
                fb = framebuf.FrameBuffer(buffer,int(self.font_size/2+bold)*ratio,self.font_size*ratio,framebuf.RGB565)
                fb.fill(bgcolor)
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size/2*ratio)-bold*ratio): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size/2):
                        if(int(fontdata[j])) & (0x80 >> int(i%(self.font_size/2))):
                            for b in range(bold+1):
                                for m in range(ratio):
                                    for n in range(ratio):
                                        fb.pixel((i+b)*ratio + m, j*ratio + n,  color)
                self._set_window(dx,dy,dx+int(self.font_size/2+bold)*ratio,dy+self.font_size*ratio)
                self.send_image_data(buffer)
                dx+=int(self.font_size/2*ratio)+bold*ratio
            else:   # 日本語の場合
                buffer = bytearray(self.font_size*(self.font_size+bold)*2*ratio*ratio)
                fb = framebuf.FrameBuffer(buffer,(self.font_size+bold)*ratio,self.font_size*ratio,framebuf.RGB565)
                fb.fill(bgcolor)
                for j in range(self.font_size):
                    if (dx > wx-int(self.font_size*ratio)-bold*ratio): # 改行の判定
                        dx=0
                        dy+=self.font_size*ratio
                    for i in range(self.font_size):
                        if(int(fontdata[j])) & (0x8000 >> int(i%(self.font_size))):
                            for b in range(bold+1):
                                for m in range(ratio):
                                    for n in range(ratio):
                                        fb.pixel((i+b)*ratio + m, j*ratio + n,  color)
                self._set_window(dx,dy,dx+(self.font_size+bold)*ratio,dy+self.font_size*ratio)
                self.send_image_data(buffer)
                dx+=int(self.font_size*ratio)+bold*ratio
            fb.fill(0)
            gc.collect()
    # 線を描く
    def line(self,sx, sy, ex, ey, color):
        """
            ブレゼンハムのアルゴリズムを使用して線をひく
        """
        # 縦横の変化量
        width = abs(ex - sx)
        height = abs(ey - sy)
        err = width - height
        # 方向
        x_dir = (sx < ex) - (sx > ex)
        y_dir = (sy < ey) - (sy > ey)
        # 同じ位置に書かないように前の値を保持
        prev_x=-1
        prev_y=-1
        while True:
            if (sx, sy) != (prev_x, prev_y): # 前回と異なる位置なら描く
                self.pset(sx, sy, color)
                (prev_x,prev_y)=(sx,sy)
            if sx == ex and sy == ey:  # 線が終点に達したら終了
                break
            e2 = err * 2
            if e2 > -height:
                err -= height
                sx += x_dir
            if e2 < width:
                err += width
                sy += y_dir
    # 四角形をかく
    def rect(self,sx,sy,width,height,color):
        """ 塗りつぶされた四角を描く"""
        (h_color,l_color) = self.color565(color) # 24bit->16bit
        self._set_window(sx,sy,sx+width,sy+height)
        self.dc(1)
        self.cs(0)
        for i in range(height):
            self.spi.write(bytearray([l_color,h_color]*width))
        self.cs(1)
        self.display_on()
        gc.collect()

    # アイコン(32x32 or 16x16)を描く
    def draw_icon(self,dx, dy, buf,color,size=32,bgcolor=0x000000,ratio=2):
        """ 開始位置(dx,dy）からbufのアイコンデータを描く、ratioは、拡大率
        画面に表示する場合には、display()を実行する """
        (h_color,l_color)=self.color565(color)
        color=(h_color << 8) | l_color
        (h_color,l_color)=self.color565(bgcolor)
        bgcolor=(h_color << 8) | l_color
        buffer = bytearray(size*size*ratio*ratio*2)
        fb = framebuf.FrameBuffer(buffer,size*ratio,size*ratio,framebuf.RGB565)
        fb.fill(bgcolor)
        if(size == 32): # 32 x 32 のアイコン用
            for j in range(64):
                for i in range(16):
                    if(int(buf[j])) & (0x8000 >> int(i%16)):
                        for m in range(ratio):
                            for n in range(ratio):
                                fb.pixel(i*ratio + 16*(j%2==1)*ratio + m, int(j/2)*ratio + n,  color)
        elif(size == 16): # 16 x 16 のアイコン用
            for j in range(16):
                for i in range(16):
                    if(int(buf[j])) & (0x8000 >> int(i%16)):
                        for m in range(ratio):
                            for n in range(ratio):
                                fb.pixel(i*ratio + m, j*ratio + n,  color)
        self._set_window(dx,dy,dx+size*ratio,dy+size*ratio)
        self.send_image_data(buffer)
        fb.fill(0)
        gc.collect()
    # ビットマップ画像ファイルを表示
    def draw_bitmap(self,file):
        """
        16bit と24bitのビットマップ表示
        24bitは1pixelずつ16bitに変換する為、処理が遅い
        """
        try:
            fp = open(file, "rb")
            fp.seek(10)
            offset=int.from_bytes(fp.read(4),'little') # 画像データの開始位置取得
            fp.seek(18)
            width=int.from_bytes(fp.read(4),'little') # 画像データの幅取得
            fp.seek(22)
            height=int.from_bytes(fp.read(4),'little') # 画像データの高さ取得
            fp.seek(28)
            bpp=int.from_bytes(fp.read(2), 'little') # 1pixelのビット数取得
            # 画面中央に表示
            sx=int((self.SCREEN_WIDTH-width)/2)
            sy=int((self.SCREEN_HEIGHT-height)/2)
            fp.seek(offset) # 画像データの開始位置に移動
            for y in range(height):
                # 描画領域の指定(1行ずつ)
                self._set_window(sx,sy+height-y,sx+width,sy+height-y+1)
                if bpp == 16: # 16ビットの場合は、そのままデータ転送
                    val = fp.read(2*width)
                    self.send_image_data(val)
                elif bpp == 24: # 24ビットの場合
                    val=bytearray()
                    for x in range(width):
                        color=int.from_bytes(fp.read(3),'little')
                        (h_color,l_color)=self.color565(color) # 24bitから16bitに変換
                        val.append(l_color)
                        val.append(h_color)
                    self.send_image_data(val) 
                else: # 16bit/24bit以外は未実装の為、処理しない
                    break
                gc.collect()
            fp.close()
        except OSError as e:
            print(f"ビットマップファイル[ {file} ]を読み込めませんでした: {e}")
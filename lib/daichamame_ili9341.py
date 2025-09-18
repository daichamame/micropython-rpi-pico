"""
   ILI9341 + XPT2046

   LCD:ILI9341
   Touch :XPT2046

   描画に関して、文字やアイコンで一部Framebufを使用しているが、
   線、四角形、ビットマップ画像は直接書き込んでいる
   色の指定は、rgbそれぞれ1バイトで、0xffffffのように24ビットの形式

"""
from machine import Pin,SPI  
import time
import framebuf
import gc

try:# フォント関連のモジュールのインポート(存在していれば)
    import daichamame_util
except ImportError:
    print("No module named 'daichamame_util'")

class ili9341(object):
    # GPIO
    # VCC
    # GND
    CS_PIN      = 9
    RST_PIN     = 13
    DC_PIN      = 8
    DIN_PIN     = 11 # MOSI(SDI)
    CLK_PIN     = 10
    # LED
    DO_PIN      = 12 # MISO(SDO)
   
    T_CLK_PIN   = 18
    T_CS_PIN	= 17
    T_DIN_PIN	= 19
    T_DO_PIN	= 16
    T_IRQ_PIN	= 20

    ILI9341_X   = 0xD0    # get x
    ILI9341_Y   = 0x90    # get y

    # 画面表示のサイズ（240 x 320） 
    WIDTH  = 240
    HEIGHT = 320
    # ボタン情報格納
    buttons = []
    
    # フォント
    font_size=16

    # ローテーション
    rotate = 0

    # タッチパネルのタッチの間隔調整(ms)
    touch_debounce_ms = 300

    # デバイスの初期処理
    def __init__(self, font_array,font_size,rotate=0):
        """
        font_array : フォントのビットマップ情報が入っている配列
        font_size : 12,14,16などのドットサイズ
        rotate : 0 90 180 270  (0は、縦が長いほうとなる)
        """
        self.rate = 4 * 1000 * 1000 # 4MHz
        self.spi = SPI(1,baudrate=self.rate, polarity=0, phase=0,sck=Pin(self.CLK_PIN),mosi=Pin(self.DIN_PIN),miso=Pin(self.DO_PIN))
        self.cs     = Pin(self.CS_PIN)
        self.dc     = Pin(self.DC_PIN)
        self.rst    = Pin(self.RST_PIN)
        self.do     = Pin(self.DO_PIN)
        self.din    = Pin(self.DIN_PIN)
        self.clk    = Pin(self.CLK_PIN)
        # touch
        self.t_rate = 200 * 1000 # 
        self.t_spi = SPI(0,baudrate=self.t_rate,polarity=0,phase=0,sck=Pin(self.T_CLK_PIN),mosi=Pin(self.T_DIN_PIN),miso=Pin(self.T_DO_PIN))
        self.t_clk	= Pin(self.T_CLK_PIN)
        self.t_cs	= Pin(self.T_CS_PIN)
        self.t_din	= Pin(self.T_DIN_PIN)
        self.t_do	= Pin(self.T_DO_PIN)
        self.t_irq	= Pin(self.T_IRQ_PIN)
        self.rotate = rotate
        self.last_time = time.ticks_ms()
        self.madctl = (rotate == 0)*0x88 + (rotate == 90)*0xE8 \
                       + (rotate == 180)*0x48 + (rotate == 270)*0x28 # 0x88 0xE8 0x48 0x28       
        self.width  = (rotate == 0 or rotate == 180)*self.WIDTH +(rotate == 90 or rotate == 270)*self.HEIGHT
        self.height = (rotate == 0 or rotate == 180)*self.HEIGHT +(rotate == 90 or rotate == 270)*self.WIDTH
        self.font_array = font_array
        self.font_size = font_size
        if font_array == None: # 機能拡張用:font_arrayが空の場合フォントライブラリをimportする
            try:
                self.util=daichamame_util.util(font_size)
            except:
                print("The module 'daichamame_util' is unavailable.")
        self.touch_flag = False
        self.init() # ディスプレイの初期処理を行う

    
    # 初期処理
    def init(self):
        """
        ディスプレイの初期化
        """
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)
        self.cs.init(self.cs.OUT, value=1)
        self.reset()

        self.send_cmd(0x01) # soft reset
        time.sleep_ms(100)
        self.send_cmd(0xCB) # power ctrl A
        self.send_data(0x39)
        self.send_data(0x2C)
        self.send_data(0x00)
        self.send_data(0x34)
        self.send_data(0x02)
        self.send_cmd(0xCF) # Power Ctrl B
        self.send_data(0x00)
        self.send_data(0x81) # 81 or C1
        self.send_data(0x30)
        self.send_cmd(0xED) # Power on sequence control
        self.send_data(0x64)
        self.send_data(0x03)
        self.send_data(0x12)
        self.send_data(0x81)
        self.send_cmd(0xE8) # Driver timing control A
        self.send_data(0x85)
        self.send_data(0x00)
        self.send_data(0x78)
        self.send_cmd(0xEA) # Driver timing control B
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_cmd(0xF7) # Pump ratio control
        self.send_cmd(0x20) # default 0x10
        self.send_cmd(0xC0) # Power ctrl 1
        self.send_cmd(0x23)
        self.send_cmd(0xC1) # Power ctrl 2
        self.send_cmd(0x10)
        self.send_cmd(0xC5) # VCOM Control 1
        self.send_cmd(0x3E)
        self.send_cmd(0x28)
        self.send_cmd(0xC7) # VCOM Control 2
        self.send_cmd(0x86)
        self.send_cmd(0xF2) # Enable 3 gamma
        self.send_data(0x00)
        self.send_cmd(0x26) # ILI9341_GAMMA_SET
        self.send_data(0x01)
        self.send_cmd(0xE0) # positive gamma correction
        self.send_image_data(bytearray([0x0f, 0x31, 0x2b, 0x0c, 0x0e, 0x08, \
                             0x4e, 0xf1, 0x37, 0x07, 0x10, 0x03, 0x0e, 0x09, 0x00 ]))
        self.send_cmd(0xE1)     # negative gamma correction
        self.send_image_data(bytearray([0x00, 0x0e, 0x14, 0x03, 0x11, 0x07, \
                             0x31, 0xc1, 0x48, 0x08, 0x0f, 0x0c, 0x31, 0x36, 0x0f ]))
        self.send_cmd(0x36) # memory access control
        self.send_data(self.madctl)
        self.send_cmd(0x3A) # pixel format
        self.send_data(0x55)
        self.send_cmd(0xB1) # frame rate; default, 70 Hz
        self.send_data(0x00)
        self.send_data(0x1B)

      
        self.send_cmd(0xB6) #
        self.send_data(0x08)
        self.send_data(0x82)
        self.send_data(0x27)

        self.send_cmd(0x11) # exit sleep

        self.send_cmd(0x30) #  partial area 
        self.send_data(0x00)
        self.send_data(0x00) # start column
        self.send_data(self.height >> 8)
        self.send_data(self.height & 0xff)

        time.sleep_ms(200)               
        self.send_cmd(0x29) # display on
        time.sleep_ms(200)
        
        self.t_cs.init(self.t_cs.OUT,value=0)
        self.t_irq.init(self.t_irq.IN,value=1)     
        self.t_irq.irq(trigger=Pin.IRQ_FALLING,handler=self.set_status)


    # HWリセット
    def reset(self):
        self.rst(1)
        time.sleep_ms(200)
        self.rst(0)
        time.sleep_ms(2)
        self.rst(1)
        time.sleep_ms(200)
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
            self.spi.write(bytearray([h_color,l_color]*self.width))
        self.cs(1)
        self.display_on()
        gc.collect()
        self.buttons=[]
        
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
        x: x座標（横軸）
        y: y座標（縦軸）
        1pixelずつ処理するため、多くの点を処理するときは遅くなる
        """
        (h_color,l_color) = self.color565(color) # 24bit->16bit
        self._set_window(x,y,x+1,y+1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([h_color,l_color]))
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
    def print( self,dx, dy, buf,color,bgcolor=0x000000,ratio=1,bold=0):
        """ 開始位置(dx,dy）
        buf:表示文字列
        color:フォントの色
        bgcolor:背景色（既定値 0x000000)
        ratio:拡大率(1,2,3)
        bold:太字（0,1,2,3)
        """
        wx=self.width
        (h_color,l_color)=self.color565(color)
        color=(l_color << 8) | h_color
        (h_color,l_color)=self.color565(bgcolor)
        bgcolor=(l_color << 8) | h_color

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
        """ 
        塗りつぶされた四角を描く
        sx : 開始X座標
        sy : 開始Y座標
        width : 幅
        height: 高さ
        color : 塗りつぶし色        
        """
        (h_color,l_color) = self.color565(color) # 24bit->16bit
        self._set_window(sx,sy,sx+width,sy+height)
        self.dc(1)
        self.cs(0)
        for i in range(height):
            self.spi.write(bytearray([h_color,l_color]*width))
        self.cs(1)
        self.display_on()
        gc.collect()

    # アイコン(32x32 or 16x16)を描く
    def draw_icon(self,dx, dy, buf,color,size=32,bgcolor=0x000000,ratio=1):
        """ 開始位置(dx,dy）からbufのアイコンデータを描く、ratioは、拡大率
        画面に表示する場合には、display()を実行する """
        (h_color,l_color)=self.color565(color)
        color=(l_color << 8) | h_color
        (h_color,l_color)=self.color565(bgcolor)
        bgcolor=(l_color << 8) | h_color
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
        16bit と24bitのビットマップ表示に対応
        24bitは1pixelずつ16bitに変換する為、処理が遅い
        file:ファイルパス
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
            sx=int((self.width-width)/2)
            sy=int((self.height-height)/2)
            fp.seek(offset) # 画像データの開始位置に移動
            for y in range(height):
                # 描画領域の指定(1行ずつ)
                self._set_window(sx,sy+height-y,sx+width,sy+height-y+1)
                if bpp == 16 or bpp == 24: # 16ビットの場合は、2bytデータ転送
                    val=bytearray()
                    for x in range(width):
                        if bpp == 16:
                            color= int.from_bytes(fp.read(2),'little')
                            h_color = (color & 0xff00) >> 8
                            l_color = color & 0x00ff
                        else:
                            color=int.from_bytes(fp.read(3),'little')
                            (h_color,l_color)=self.color565(color) # 24bitから16bitに変換
                        val.append(h_color)
                        val.append(l_color)
                    self.send_image_data(val) 
                else: # 16bit/24bit以外は未実装の為、処理しない
                    break
                gc.collect()
            fp.close()
        except OSError as e:
            print(f"ビットマップファイル[ {file} ]を読み込めませんでした: {e}")
    # XY値の取得
    def read_data(self,ch):
        """
        タッチの値を読む
        ch : ILI9341_X/ILI9341_Y
        """
        readbuffer=bytearray(4)
        self.t_cs(0)
        self.t_spi.write_readinto( bytes([ch]) + b'\x00\x00\x00' ,readbuffer)
        time.sleep_ms(1)
        self.t_cs(1)
        
        val = (((readbuffer[1] << 8) | (readbuffer[2])) >> 3) & 0x0FFF
       
        if ch == self.ILI9341_X:
            val = val*self.WIDTH/4095
        else:
            val = val*self.HEIGHT/4095
        return int(val)
    # 値の平均値を計算
    def read_data_avg(self,ch):
        """
        10回取得し平均値を取得する
        """
        val=[0]*10 # 10回取得
        for cnt in range(10):
            val[cnt]=self.read_data(ch)
            time.sleep_ms(1)
        sorted_val = sorted(val)
        trim_val = sorted_val[1:-1]  # 最小と最大を除く
        avg = sum(trim_val) / len(trim_val)
        return int(avg)
    # x y の値を取得
    def read_touch_position(self):
        """
        タッチした値を取得する
        センサーから取得した値を画面の回転に合わせて変換する
        戻り値：
        True/False : 取得/未取得
        rx : x座標
        ry : y座標
        hit_indexes : buttonsに設定されたボタン情報からどのボタンが押されたか判定
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time,self.last_time) > self.touch_debounce_ms: # タッチセンサーの連打防止用に１秒以内の連続タッチを除外
            self.last_time = current_time
            # x,y 平均値を取得
            x=self.read_data_avg(self.ILI9341_X)
            y=self.read_data_avg(self.ILI9341_Y)
            # 画面のローテーションに合わせてx yを変換する
            rx=y*(self.rotate==90)+(self.width-x)*(self.rotate==0)+(self.width-y)*(self.rotate==270)+x*(self.rotate==180)
            ry=x*(self.rotate==90)+             y*(self.rotate==0)+(self.height-x)*(self.rotate==270)+(self.height-y)*(self.rotate==180)
            # ボタンのインデックス取得
            hit_indexes = [i for i, (bx, by, bw, bh,lb,color,bgcolor) in enumerate(self.buttons)
               if bx <= rx < bx + bw and by <= ry < by + bh]
            return (True,rx,ry,hit_indexes)
        return (False,0,0,0)
    
    # flag set
    def set_status(self,t):
        """
        タッチパネルが押されたときのフラグ
        このフラグがTrueとなったときに、read_touch_position処理を実行する
        """
        self.touch_flag = True
    
    # simple button
    def add_button(self,x,y,w,h,label,color,bgcolor):
        """ 
        簡易ボタン関数
        x,y :スタート座標 w,h:幅と高さ
        ボタンを描画すると、ボタン配列に登録される
        read_touch_positionを実行すると、押されたボタンを判別できる
        """ 
        self.rect(x,y,w,h,bgcolor) # 四角形を書く
        self.print(x,int(y+h/2-self.font_size*2/2),label,color,bgcolor,ratio=2,bold=1) # 文字を書く
        self.buttons.append([x,y,w,h,label,color,bgcolor]) # ボタンリストに登録する
        return len(self.buttons) - 1 # ボタンのインデックス番号を返す

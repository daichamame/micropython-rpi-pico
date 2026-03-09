"""
モジュール名: ir_nec_ssd1306.py
概要:
    NEC方式 赤外線リモコン受信モジュールを使用して
    リモコンのアドレスとコマンドを取得してOLEDに表示します。

使用デバイス:
    以下のデバイスを使用して作成しています
    表示：
      SSD1306
    送信：
      ＮＥＣフォーマット準拠 赤外線リモコン送信機 
    受信：
      赤外線リモコン受信モジュール OSRB38C9AA
接続：
  SSD1306は、I2C CH:0 SDA=GP4,SCL=GP5,FREQ=400kHz
  OSRB38C9AAは、OUTPUT:GP16

配置：
    ir_nec_ssd1306.py (このファイル)
    lib\
        daichamame_ir_nec_decoder.py
        daichamame_ssd1306.py
        fontloader.py
    font\
        shnm8x16r.bdf(東雲フォント)
"""
import daichamame_ir_nec_decoder
import daichamame_ssd1306
import fontloader
from machine import Timer

class MainClass:
    def __init__(self):
        # フォントの読み込み
        fl=fontloader.FontLoader("/font/shnm8x16r.bdf")
        fntdata=fl.load_font()
        # OLEDの初期化
        self.ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=fntdata,font_size=16,ch=0,scl_pin=5,sda_pin=4)
        self.ssd1306.init()
        self.ssd1306.clear()
        self.ssd1306.flash()
        self.ir = daichamame_ir_nec_decoder.IRNECReceiver(pin=16)
        self.addr = 0xff
        self.cmd = 0xff        
        self.ssd1306.print(0, 16,"Address:Command",1)
        self.update_display()
        # タイマーの初期化
        self.timer = Timer()
        # タイマーを設定（100ms毎にリモコンの状態をチェックし描画する）
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=self.main_loop)

    # OLED初期描画
    def update_display(self):
        text = "0x{:02X}   :0x{:02X}".format(self.addr,self.cmd)
        self.ssd1306.print(0, 32,text,1)
        self.ssd1306.display() 
        
    # メインループ
    def main_loop(self,t):
        val = self.ir.read()    # リモコンの押下状況を取得
        if val is not None: # リモコンが押されていれば、描画処理を実施
            (self.addr, self.cmd) = val
            self.update_display()

# メイン
if __name__ == "__main__":

    mainapp = MainClass() # メインアプリ起動
    

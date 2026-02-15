"""
モジュール名: ir_nec_ssd1306.py
概要:
    NEC方式 赤外線リモコン受信モジュールを使用して
    パルス幅の計測・リーダー検出・0/1判定・32bit整合性チェックを行い、値を返す。
    値によるキー判定は本モジュールでは行わない。
特徴:
    - IRQでリアルタイムにパルス幅を計測し、最新の値を保持
    - 値の取得は read() を呼ぶだけで最新の値を取得可能

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
    keycode = {
        0x1B:"Power",
        0x1F:"  A",
        0x1E:"  B",
        0x1A:"  C",
        0x8D:" UL",      # 左上
        0x05:" Up",
        0x84:" UR",      # 右上
        0x08:"Left",
        0x04:"Center",
        0x01:"Right",
        0x88:" LL",      # 左下
        0x00:"Down",
        0x81:" LR"       # 右下
    }
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
        self.datacode = 0xff
        self.update_display()
        # タイマーの初期化
        timer = Timer()
        # タイマーを設定（100ms毎にリモコンの状態をチェックし描画する）
        timer.init(period=100, mode=Timer.PERIODIC, callback=self.main_loop)

    # OLED初期描画
    def update_display(self):
        self.ssd1306.clear()
        keyname = self.keycode.get(self.datacode, '-----')
        self.ssd1306.print(0, 16,keyname,2)
        self.ssd1306.display() 
        
    # メインループ
    def main_loop(self,t):
        val = self.ir.read()    # リモコンの押下状況を取得
        if val: # リモコンが押されていれば、描画処理を実施
            (addr, cmd) = val
            self.datacode = cmd
            self.update_display()

# メイン
if __name__ == "__main__":

    mainapp = MainClass() # メインアプリ起動
    
"""

赤外線リモコンで操作する FM DSP ラジオ

概要
  赤外線リモコンで制御するDSPラジオ

使用した部品
  ・Raspberry Pi Pico
  ・OLED（SSD1306 I2C）
  ・FMラジオモジュール RDA5807H  
  ・ステレオミニジャック（アンテナ兼用）
  ・赤外線リモコン OE13KIR
  ・赤外線受信モジュール OSRB38C9AA
  ・ブレッドボード、ジャンパーワイヤー
  ・タクトスイッチ（リセット用）
  ・イヤホンまたはスピーカー（1m 程度のケーブルがアンテナ代わり）

配線
  ・SSD1306：I2C0（SDA=GP4, SCL=GP5, 400kHz）
  ・RDA5807H：I2C0（同上）
  ・IR 受信：GP16
  ・RDA5807H の LR 出力 → ステレオミニジャック
  ・アンテナ：ミニジャックの GND に接続（ケーブルがアンテナになる  
機能
  ・リモコンの左右キーで局を切り替え
  ・上下キーで音量調整（0〜15）
  ・OLED に局名・周波数・音量を表示
  ・NEC 赤外線コードを daichamame_ir_nec_decoder でデコード
  ・タイマー割り込み（100ms）でイベント駆動

"""
import daichamame_rda5807
import daichamame_ssd1306
import daichamame_ir_nec_decoder
import fontloader
import machine


class MainClass:
    # 変数
    vol     = 1 # ボリューム（0-15）
    ct      = 0 # 周波数の番号
    freq    = [80.0,81.3,82.5,90.5,91.6,93.0] # 東京のラジオ局
    # 上書き表示をするため空白を含めて10文字で定義
    fm_name = ["TOKYO FM  ","J-WAVE    ","NHK-FM    ","TBSﾗｼﾞｵ    ","ﾌﾞﾝｶﾎｳｿｳ  ","ﾆｯﾎﾟﾝﾎｳｿｳ "]
    # 赤外線リモコン OE13KIRのキーとコード
    #     0x1B:電源、0x1F:A、0x1E:B、0x1A:C
    #     0x8D:左上、0x05:上、0x84:右上
    #     0x08:左、0x04:中央、0x01:右
    #     0x88:左下、0x00:下、0x81:右下
    def __init__(self):
        # フォントの読み込み
        fl=fontloader.FontLoader("/font/shnm8x16r.bdf")
        fntdata=fl.load_font()
        # 赤外線受信の初期化
        self.ir = daichamame_ir_nec_decoder.IRNECReceiver(pin=16)
        self.datacode = 0xff
        # OLEDの初期化
        self.ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=fntdata,font_size=16,ch=0,scl_pin=5,sda_pin=4)
        self.ssd1306.init()
        self.ssd1306.clear()
        self.ssd1306.flash()
        # RDA5807の初期化
        self.radio = daichamame_rda5807.RDA5807(ch=0,scl_pin=5,sda_pin=4,frequency=400000)
        self.radio.init()
        self.radio.set_volume(self.vol) # ボリュームの設定      
        self.radio.set_freq(self.freq[self.ct]) # 周波数の設定
        self.update_display()
        
        # タイマーの初期化
        timer = machine.Timer()
        # タイマーを設定
        timer.init(period=100, mode=machine.Timer.PERIODIC, callback=self.main_loop)           
        
    # OLED初期描画
    def update_display(self):
        self.ssd1306.print(100, 0,"{:02}".format(self.vol),1)     # 音量
        self.ssd1306.print(  4, 0,self.fm_name[self.ct],1)        # 局
        self.ssd1306.print(  0,16,str(self.freq[self.ct]),3)      # 周波数
        self.ssd1306.print(100,48,"MHz",1)                        # 単位
        self.ssd1306.display()  # 画面表示

    # メインループ
    def main_loop(self,t):
        try:
            val = self.ir.read()    # リモコンの押下状況を取得
            if val:
                (addr,cmd) = val
                if cmd == 8 : # リモコンの左が押された
                    self.ct = (self.ct-1)*(self.ct > 0) + (len(self.freq) -1 )*(self.ct ==0)
                    self.radio.set_freq(self.freq[self.ct])                  # 周波数の設定
                    self.update_display()
                if cmd == 1 : # リモコンの右が押された
                    self.ct = (self.ct+1)*(self.ct < len(self.freq)-1)
                    self.radio.set_freq(self.freq[self.ct])                  # 周波数の設定
                    self.update_display()
                if cmd == 5 : # リモコンの上が押された
                    self.vol = (self.vol+1)*(self.vol < 15)+(self.vol==15)*15
                    self.radio.set_volume(self.vol)                          # 音量の設定
                    self.update_display()
                if cmd == 0 : # リモコンの下が押された
                    self.vol = (self.vol-1)*(self.vol > 0)
                    self.radio.set_volume(self.vol)                          # 音量の設定
                    self.update_display()
        except Exception as e:
            print("Error in timer:", e)


# メイン
if __name__ == "__main__":

    mainapp = MainClass() # メインアプリ起動
    



"""
    Ili9341 + xpt2046 と RDA5807 をつかったラジオ

    接続：
    Ili9341 + xpt2046
    RDA5807は、I2C CH:0 SDA=GP4,SCL=GP5,FREQ=100kHz

    モジュール：
    daichamame_ili9341
    daichamame_rda5807
    daichamame_net
    fontloader    

    使用フォント：
    東雲フォントのshnm8x16r.bdf

    プログラム中のenv.SSID,env.ENCRYPTION_KEY,env.NTP_SERVER,env.URLは、
    設定情報としてファイル名:env.pyに以下の3行を書いて配置
    -----------------------------------------------
    SSID="2.4GHzのSSID"
    ENCRYPTION_KEY="暗号化キー"
    NTP_SERVER="NTPサーバのアドレス"
    -----------------------------------------------

このプログラムは、割り込みで動作する常駐型です

"""
import daichamame_ili9341
import daichamame_rda5807
import daichamame_net
import fontloader
import machine

import env # ssid ,encryption_key,ntp server


class MainClass:
    # 変数
    vol = 5 # ボリューム（0-15）
    ct = 0 # 周波数の番号
    freq = [80.0,81.3,82.5,90.5,91.6,93.0] # 東京のラジオ局
    fm_name = ["TOKYO FM ","J-WAVE","NHK-FM","TBSﾗｼﾞｵ","ﾌﾞﾝｶ ﾎｳｿｳ","ﾆｯﾎﾟﾝ ﾎｳｿｳ"]
    time_count = 0 # 時刻カウント用
    # 音量アイコン(16x16)
    vol_icon=(
        [0x0000,0x0000,0x0600,0x0E00,0x1E00,0x1E00,0x7E00,0x7E00,0x7E00,0x7E00,0x1E00,0x1E00,0x0E00,0x0600,0x0000,0x0000],#音声0
        [0x0000,0x0000,0x0600,0x0E00,0x1E00,0x1E00,0x7E80,0x7E80,0x7E80,0x7E80,0x1E00,0x1E00,0x0E00,0x0600,0x0000,0x0000],#音声1
        [0x0000,0x0000,0x0600,0x0E00,0x1E20,0x1E20,0x7EA0,0x7EA0,0x7EA0,0x7EA0,0x1E20,0x1E20,0x0E00,0x0600,0x0000,0x0000],#音声2
        [0x0000,0x0000,0x0608,0x0E08,0x1E28,0x1E28,0x7EA8,0x7EA8,0x7EA8,0x7EA8,0x1E28,0x1E28,0x0E08,0x0608,0x0000,0x0000],#音声3
        [0x0000,0x0002,0x060A,0x0E0A,0x1E2A,0x1E2A,0x7EAA,0x7EAA,0x7EAA,0x7EAA,0x1E2A,0x1E2A,0x0E0A,0x060A,0x0002,0x0000],#音声4
    )

    def __init__(self):
        # RDA5807の初期化
        self.radio = daichamame_rda5807.RDA5807(ch=0,scl_pin=5,sda_pin=4,frequency=100000)
        self.radio.init() # ラジオの初期化
        self.radio.set_volume(self.vol) # ボリュームの設定
        self.radio.set_freq(self.freq[self.ct]) # 周波数の設定
        # LCD
        # /font/フォルダに 東雲フォントのshnm8x16r.bdfを表示用に利用
        fnt=fontloader.FontLoader("/font/shnm8x16r.bdf")
        shnmfont=fnt.load_font() # フォントデータを読み込む       
        self.lcd=daichamame_ili9341.ili9341(font_array=shnmfont,font_size=16,rotate=0)
        # タイマーの初期化
        timer = machine.Timer()
        # LCD初期描画
        self.lcd.clear()
        self.update_volume()
        self.update_freq()
        self.lcd.add_button(  0,240,80, 40,"  - ",0xffffff,0x191970)
        self.lcd.print(90,240,"VOL",0xffffff,ratio=2,bold=2)
        self.lcd.add_button(160,240,80, 40,"  + ",0xffffff,0x191970)
        self.lcd.add_button(  0,280,80, 40," << ",0xffffff,0x197019)
        self.lcd.print(80,280," CH",0xffffff,ratio=2,bold=2)
        self.lcd.add_button(160,280,80, 40," >> ",0xffffff,0x197019)
        self.update_datetime(0)
        # タイマーを設定(200msおきに時刻表示と、タッチパネルを押された場合の処理)
        timer.init(period=200, mode=machine.Timer.PERIODIC, callback=self.main_loop)
    # タイマーループ
    def main_loop(self,t):
        if self.time_count == 5*60 : # １分おきに時刻を更新
            self.update_datetime(t)
            self.time_count = 1
        else:
            self.time_count += 1
        self.touch(t)
        
    # 時刻更新
    def update_datetime(self,t):
        rtc = machine.RTC()
        ctime=rtc.datetime() # 現在時刻を取得
        self.time_count = 5*ctime[6] # 0秒で更新できるように調整
        self.lcd.print(0,0,"{:4d}/{:2d}/{:2d}".format(ctime[0],ctime[1],ctime[2]),0xffffff,ratio=2,bold=1)
        self.lcd.print(70,40,"{:2d}:{:02d}".format(ctime[4],ctime[5]),0xffffff,ratio=3,bold=2)

    # ボリューム表示
    def update_volume(self):
        self.lcd.draw_icon(190,  0,self.vol_icon[int((self.vol+1)/4)],0xc0c060,16,ratio=2)
        self.lcd.print(222,8,"{:02d}".format(self.vol),0xc0c060)
        
    # チャンネル表示
    def update_freq(self):
        self.lcd.print( 10,150,str(self.freq[self.ct]),0xffa500,ratio=4,bold=3)
        self.lcd.print(190,180,"MHz",0xffa500,ratio=2)        
        self.lcd.rect(0,110,240,32,0x000000)
        self.lcd.print(  0,110,str(self.fm_name[self.ct]),0x32cd32,bold=2,ratio=2)

    # main
    def touch(self,t):
        if self.lcd.touch_flag == True:
            (status,x,y,hit)=self.lcd.read_touch_position()
            if status == True and len(hit)>0:
                # ボリューム変更
                if hit[0] == 0:
                    self.vol = self.vol-(self.vol>0)
                    self.radio.set_volume(self.vol) # ボリュームの設定
                    self.update_volume() # ボリュームアイコン更新
                elif hit[0] == 1:
                    self.vol = self.vol+(self.vol<15)
                    self.radio.set_volume(self.vol) # ボリュームの設定
                    self.update_volume() # ボリュームアイコン更新
                # チャンネル選択
                elif hit[0] == 2:
                    self.ct = self.ct-(self.ct>0)
                    self.radio.set_freq(self.freq[self.ct]) # 周波数の設定
                    self.update_freq() # チャンネル表示
                elif hit[0] == 3:
                    self.ct = self.ct+(self.ct<len(self.freq)-1)
                    self.radio.set_freq(self.freq[self.ct]) # 周波数の設定
                    self.update_freq() # チャンネル表示
            self.lcd.touch_flag = False

        
# メイン
if __name__ == "__main__":

    # wifi接続　2.4 GHzの802.11 b/g/nに対応
    wifi = daichamame_net.net()
    wifi.connect_to_wifi(ssid=env.SSID,encryption_key=env.ENCRYPTION_KEY)
    # RTCの初期値にNTPサーバから取得した時刻をJSTで登録
    wifi.set_time_jst(env.NTP_SERVER)
    rtc = machine.RTC()
    mainapp = MainClass() # メインアプリ起動




        




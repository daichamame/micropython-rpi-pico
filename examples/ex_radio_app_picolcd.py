"""
    Waveshare Pico LCD 1.3 で操作する FMラジオ

    接続：
    Pico LCD 1.3
    RDA5807は、I2C CH:0 SDA=GP4,SCL=GP5,FREQ=100kHz

    モジュール：
    daichamame_picolcd13
    daichamame_rda5807
    daichamame_net
    fontloader    

    使用フォント：
    東雲フォントのshnm8x16r.bdf

    プログラム中のenv.SSID,env.ENCRYPTION_KEY,env.NTP_SERVER,env.URLは、
    設定情報としてファイル名:env.pyに以下を書いて配置
    -----------------------------------------------
    SSID="2.4GHzのSSID"
    ENCRYPTION_KEY="暗号化キー"
    NTP_SERVER="NTPサーバのアドレス"
    -----------------------------------------------

このプログラムは、すべて割り込みで動作する常駐型です

"""
import micropython
import daichamame_picolcd13
import daichamame_rda5807
import daichamame_net
import fontloader
import time
import os
import gc
from machine import Pin,SPI 

import env # ssid ,encryption_key,ntp server


class MainClass:
    # 変数
    vol = 10 # ボリューム（0-15）
    ct = 0 # 周波数の番号
    freq = [80.0,81.3,82.5,90.5,91.6,93.0] # 東京のラジオ局
    # ラジオ局名は、最大長に合わせて空白で埋めること
    fm_name = ["TOKYO FM  ","J-WAVE    ","NHK-FM    ","TBSﾗｼﾞｵ   ","ﾌﾞﾝｶ ﾎｳｿｳ ","ﾆｯﾎﾟﾝ ﾎｳｿｳ"]
    last_time = 0 # 前回押したボタンの時間保持用
    mute_on = False
    display_on = True  # True:on False:off
    time_sec_on = False # 時刻の秒表示 True:on False:off
    sleep_time = 60 #画面表示オフのカウント
    sleep_count = 0 # 画面表示オフまでのカウント
    reset_count = False # 
    update_area = 15 # 1:date,2:time,4:freq,8:sound 16:system
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
        self.lcd=daichamame_picolcd13.PICOLCD13(font_array=shnmfont,font_size=16,rotate=90)
        self.rtc = machine.RTC()
        self.ctime=self.rtc.datetime() # 現在時刻を取得
        # ボタンを押したときに関数を実行
        self.lcd.key_a.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.key_b.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.key_x.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.key_y.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.joy_u.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.joy_d.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.joy_l.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.joy_r.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.joy_c.irq(trigger=Pin.IRQ_FALLING,handler=self.button_pressed)
        self.lcd.clear()
        # 時刻タイマーの設定（1sおきに時刻取得)
        self.date_timer = machine.Timer()
        self.date_timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self.update_datetime)
        # 画面表示タイマーの設定(200msおきに表示関数を実行)
        self.display_timer = machine.Timer()
        self.display_timer.init(period=200, mode=machine.Timer.PERIODIC, callback=self.main_loop)

    # ボタンを押したときの処理を作成
    def button_pressed(self,p):
        self.sleep_count = 0 # ボタンが押されたら0
        try:              
            # ボリューム変更
            if p == self.lcd.joy_u or p == self.lcd.joy_d:
                self.vol = self.vol+(p==self.lcd.joy_u)*(self.vol<15)-(p == self.lcd.joy_d)*(self.vol>0)
                self.radio.set_volume(self.vol) # ボリュームの設定
                self.update_area |= 0x08
            if p == self.lcd.joy_l or p == self.lcd.joy_r:
                self.ct = self.ct-(p == self.lcd.joy_l)*(self.ct>0)+(p == self.lcd.joy_r)*(self.ct<len(self.freq)-1) # 表示周波数の計算
                self.radio.set_freq(self.freq[self.ct]) # 周波数の設定
                self.update_area |= 0x04
            # システム情報表示
            if p == self.lcd.key_a:
                self.update_area = 0x10
            # 時計の秒表示／非表示
            elif p == self.lcd.key_b:
                self.time_sec_on = not self.time_sec_on 
                self.update_area |= 0x02
            # 画面の表示/非表示切り替え
            elif p == self.lcd.key_x:
                self.display_on = not self.display_on
                if self.display_on == True:
                    self.lcd.display_on() # 画面表示
                else:
                    self.lcd.display_off() # 画面非表示
            # ミュート(ミート機能ではなく一時的に音量0)
            elif p == self.lcd.key_y:
                self.mute_on = not self.mute_on
                if self.mute_on == True:
                    self.radio.set_volume(0) # ボリュームの設定
                else:
                    self.radio.set_volume(self.vol) # ボリュームの設定
        except Exception as e:
            print("Error in IRQ:", e)

    # メインループ
    def main_loop(self,t):
        try:
            # 日付の更新
            if self.update_area & 0x01:
                self.lcd.print(0,0,"{:4d}/{:2d}/{:2d}".format(self.ctime[0],self.ctime[1],self.ctime[2]),0x00bfff,bold=1)
            # 時刻の更新
            if self.update_area & 0x02:
                if self.time_sec_on == True: # 秒表示
                    self.lcd.print(0,40,"{:2d}:{:02d}:{:02d}".format(self.ctime[4],self.ctime[5],self.ctime[6]),0x00bfff,ratio=3,bold=2)
                else: # 分が更新された時か、表示モードが更新されたときに描画
                    self.lcd.print(0,40,"  {:2d}:{:02d} ".format(self.ctime[4],self.ctime[5]),0x00bfff,ratio=3,bold=2)
            # ラジオ局の更新
            if self.update_area & 0x04:
                self.lcd.print( 10,150,str(self.freq[self.ct]),0xffd700,ratio=4,bold=3)
                self.lcd.print(190,180,"MHz",0xffa500)        
                self.lcd.print(  0,110,self.fm_name[self.ct],0x7fffd4,bold=2)
                self.display_on=True
                self.lcd.display_on()
            # 音量の更新
            if self.update_area & 0x08:
                self.lcd.draw_icon(200,  0,self.vol_icon[int((self.vol+1)/4)],0xc0c060,16)
            # システム情報の表示
            if self.update_area == 0x10:
                self.system_info()  # システム情報の表示
                self.update_area |= 0x0F # 時刻とラジオ局表示
                return
            self.update_area = 0
        except Exception as e:
            print("Error in Timer:", e)
    # 時刻取得
    def update_datetime(self,t):
        self.ctime=self.rtc.datetime() # 現在時刻を取得
        # 日付が変わったとき=時分秒が0　日付更新フラグオン
        if(self.ctime[4] == 0 and self.ctime[5] == 0 and self.ctime[6] == 0):
            self.update_area |= 0x01
        # 秒表示または、分が変わったとき(秒が0) 時刻更新フラグオン
        if(self.time_sec_on == True or (self.time_sec_on == False and self.ctime[6] == 0)):
            self.update_area |= 0x02
        self.sleep_count += 1
        # 無操作時間が指定時間経過したら画面非表示
        if self.sleep_count == self.sleep_time:
            self.lcd.display_off() # 画面非表示
            self.display_on = False     
    # システム情報表示
    def system_info(self):
        self.lcd.clear()
        gc.collect()
        mem_free=gc.mem_free()
        mem_alloc=gc.mem_alloc()
        mem_total=mem_free + mem_alloc
        self.lcd.print(0,  0,"RAM--------------------",0xffffff,ratio=1)
        self.lcd.print(0, 16,"Size : {:3d} Kb".format(int(mem_total/1024)),0xffffff)
        self.lcd.print(0, 48,"Used : {:3d} Kb".format(int(mem_alloc/1024)),0xffffff)
        self.lcd.print(0, 80,"Free : {:3d} Kb".format(int(mem_free/1024)),0xffffff)
        stat = os.statvfs("/")
        size = stat[1] * stat[2]
        free = stat[0] * stat[3]
        used = size - free
        self.lcd.print(0,128,"File System------------",0xffffff,ratio=1)
        self.lcd.print(0,142,"Size : {:3d} Kb".format(int(size/1024)),0xffffff)
        self.lcd.print(0,174,"Used : {:3d} Kb".format(int(used/1024)),0xffffff)
        self.lcd.print(0,208,"Free : {:3d} Kb".format(int(free/1024)),0xffffff)
        time.sleep(3)
        # LCD初期描画
        self.lcd.clear()
        
# メイン
if __name__ == "__main__":

    # wifi接続　2.4 GHzの802.11 b/g/nに対応
    wifi = daichamame_net.net()
    wifi.connect_to_wifi(ssid=env.SSID,encryption_key=env.ENCRYPTION_KEY)
    # RTCの初期値にNTPサーバから取得した時刻をJSTで登録
    wifi.set_time_jst(env.NTP_SERVER)
    mainapp = MainClass() # メインアプリ起動





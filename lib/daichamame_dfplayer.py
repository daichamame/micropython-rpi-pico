"""
    DF Player mini
    UART
    フォルダ名は、00-99
    ファイル名は、先頭3文字が数字で後ろは日本語でも可
"""
from machine import Pin, UART
import time

class DFPLAYER(object):
    def __init__(self,uart_tx=None,uart_rx=None):
        """使用するピンの初期化"""
        if(uart_tx is None or uart_rx is None):
            # default pin 
            self.uart=UART(0,baudrate=9600,bits=8,tx = Pin(0),rx = Pin(1))
        else:
            self.uart=UART(0,baudrate=9600,bits=8,tx = Pin(uart_tx),rx = Pin(uart_rx))
     # コマンドを送信する
    def send_cmd(self, cmd,param1=0x00,param2=0x00):
        """ Format: $S=0x7E VER=0xFF Len=0x06
                    CMD Feedback 1:feedback 0:no feedback
                    param1 param2 checksum_h checksum_l $O=0xEF
        """
        buf=bytearray()
        feedback = 0x00 # feedbackなし
        checksum = 0xFFFF-(0xFF + 0x06 + cmd + feedback + param1 + param2 ) + 1
        checksum_h = checksum >> 8
        checksum_l = checksum & 0xff
        sdata = bytearray([0x7E,0xFF,0x06,cmd,feedback,param1,param2,checksum_h,checksum_l,0xEF])
        # コマンドを実行
        self.uart.write(sdata)
        time.sleep_ms(100)
        # 戻り値を取得
        rdata = self.uart.read(10)
        if(rdata is not None):
            return (rdata[5] << 8) + rdata[6]
        else:
            #　None
            return None
   
    # 0x01 次の曲再生
    def next_music(self):
        """再生中に次の曲"""
        self.send_cmd(0x01,0x00,0x00)
    # 0x02 前の曲再生
    def prev_music(self):
        """再生中に前の曲"""
        self.send_cmd(0x02,0x00,0x00)
    # 0x03 再生（現在のトラックから再生）
    def play(self,no=None):
        """ 現在選曲の曲か、番号を指定して再生 """
        if(no is None):
            no = self.get_track()
        self.send_cmd(0x03,0x00,no)
        self.start() # 再生
    # 0x04 ボリュームをあげる
    def inc_volume(self):
        self.send_cmd(0x04,0x00,0x00)
    # 0x05 ボリュームをさげる
    def dec_volume(self):
        self.send_cmd(0x05,0x00,0x00)
    # 0x06 音量設定 (0-30)
    def set_volume(self,val):
        """ val:0-30 """
        if(val >= 0 and val <= 30):
            self.send_cmd(0x06,0x00,val)
    # 0x07 イコライザー設定 (0-5)
    def set_equalizer(self,val):
        """ val: 0:normal 1:pop 2:rock 3:jazz 4:classic 5:base """
        if(val >= 0 and val <= 5):
            self.send_cmd(0x07,0x00,val)
    # 0x08 シングルリピート
    def set_repeat_play_single(self,param):
        """ 指定した曲を繰り返し再生 playmode:2"""
        self.send_cmd(0x08,0x00,param)
    # 0x09 再生メディア指定
    def set_media(self):
        """0:U 1:TF 2:AUX 3:SLEEP 4:FLASH """
        self.send_cmd(0x09,0x00,0x01)
    # 0x0C リセット
    def reset(self):
        self.send_cmd(0x0C)
        time.sleep_ms(3000)
    # 0x0D スタート
    def start(self):
        self.send_cmd(0x0D)
    # 0x0E 一時停止
    def pause(self):
        """ 現在再生中の曲を一時停止する """
        self.send_cmd(0x0E)
    # 0x0F 曲指定再生
    def specify_play(self,folder,fileno):
        """ フォルダおよびファイル名を指定して再生
            folder:00-99 fileno:0-255
        """
        self.send_cmd(0x0F,folder,fileno)
    # 0x11 繰り返し再生(1:play)
    def set_repeat_play(self):
        """ 曲の1曲目から再生　playmode:0 """
        self.send_cmd(0x11,0x00,0x01)
    # 0x17 フォルダ内繰り返し再生
    def set_repeat_play_folder(self,folder):
        """ 指定したフォルダ内を繰り返し再生 playmode:1 """
        self.send_cmd(0x17,0x00,folder)
        time.sleep_ms(1500)
    # 0x18 ランダム再生
    def set_random_play(self):
        """ 曲の1曲目から再生 playmode:3 """
        self.send_cmd(0x18)
    # 0x42 ステータス
    def get_status(self):
        """音楽の再生状態を取得 """
        val=self.send_cmd(0x42,0x00,0x00)
        return val
    # 0x43 音量取得
    def get_volume(self):
        """現在の音量"""
        val=self.send_cmd(0x43,0x00,0x00)
        return val
    # 0x44 イコライザー取得
    def get_equalizer(self):
        """現在のイコライザー"""
        val=self.send_cmd(0x44,0x00,0x00)
        return val
    # 0x45 プレイモード取得
    def get_playmode(self):
        """再生のプレイモードを取得"""
        val=self.send_cmd(0x45,0x00,0x00)
        return val
    # 0x48 TF-card ファイル数取得
    def get_total_count(self):
        """ TF-card ファイル数取得 """
        val=self.send_cmd(0x48,0x00,0x00)
        return val
    # 0x4B TF-card 現在のトラック
    def get_track(self):
        """ TF-card 現在のファイル """
        val=self.send_cmd(0x4B,0x00,0x00)
        return val


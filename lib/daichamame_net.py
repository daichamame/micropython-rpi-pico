"""
    ネットワークに関連するライブラリ（Raspberry Pi pico w 向け)
    WiFi接続
    NTP,HTTP
"""
import requests
import network
import time
import socket
import struct
import machine

class net(object):
    
    # 初期処理
    def __init__(self):
        self.wlan = ()
    # WiFiに接続する
    def connect_to_wifi(self,ssid,encryption_key):
        """ SSIDと暗号化キーを設定します """
        self.wlan = network.WLAN(network.STA_IF) # ネットワークインターフェースオブジェクト作成
        self.wlan.active(True)                   # 有効化 
        if (self.wlan.isconnected() == False):   # 接続していない場合
            self.wlan.connect(ssid, encryption_key)  # 接続する
            while not self.wlan.isconnected():
                time.sleep(1)
    
        return self.wlan.ifconfig()
    # WiFiを切断する
    def disconnect_from_wifi(self):
        self.wlan.disconnect()

    # RTCの初期値にNTPサーバから取得したJSTの時刻を登録
    def set_time_jst(self,server):
        # 1900/1/1から1970/1/1まで秒数
        ntp_delta = 2208988800 
        # 最初のバイトを0x1b (LI=0, VN=3, Mode=3) に設定し、残りの47バイトを0にする
        ntp_query =  b'\x1b' + 47 * b'\0'
        # IPアドレス変換し、アドレスを取得
        addr = socket.getaddrinfo(server, 123)[0][4]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(ntp_query, addr)
        recv = sock.recv(48)
        sock.close()
        # NTPレスポンスからTransmit Timestamp（T3）を抽出
        val = struct.unpack("!I", recv[40:44])[0]
        # 1970/1/1からの秒数を取得
        ntp_sec = val - ntp_delta + 9*60*60
        ntime = time.localtime(ntp_sec)
        rtc = machine.RTC()
        rtc.datetime((ntime[0], ntime[1], ntime[2],ntime[6],ntime[3], ntime[4], ntime[5],0))
        return 

    # HTTPリクエスト(ファイル出力)
    def https_request_to_file(self,url,max_size=32768,filename="output.txt"):
        """
        httpリクエスト結果をmax_sizeバイトまでファイル出力をします。
        """
        buffer_size = 0
        try:
            with open(filename, "wb") as file: # 書き込みファイルを開く
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    while True:
                        chunk = response.raw.read(1024)  # 必要に応じて調整
                        if not chunk or buffer_size > (max_size - 1024):
                            break
                        buffer_size += len(chunk)
                        file.write(chunk)
                response.close()
        except Exception as e:
            print(f"Error occurred: {e}")
    # HTTPリクエスト(バッファ出力)
    def https_request(self,url,max_size=16384):
        """
        httpリクエスト結果をmax_sizeバイトまでバッファに読み込みます。     
        """
        buffer=bytearray()
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                while True:
                    chunk = response.raw.read(1024)  # チャンクを直接読み込む
                    if not chunk or len(buffer) > max_size - 1024:
                        break
                    buffer.extend(chunk)
            response.close()
            return buffer    
        except Exception as e:
            print(f"Error occurred: {e}")
        return None
    
    
"""
    Raspberry Pi pico W に接続したSSD1306に日付と時刻を表示する
    NTPサーバから時刻を取得し、その後RTCにJSTの時刻をセットする
    1分間に1度秒数が0になったタイミングで画面表示を更新する
    （秒単位でも更新可能だが、デバイスへの負荷を考えて1分間に1度としている)

    プログラム中のenv.SSID,env.ENCRYPTION_KEY,env.NTP_SERVER,env.URLは、
    設定情報としてファイル名:env.pyに以下の4行を書いて、アップロードしてます。
    -----------------------------------------------
    SSID="2.4GHzのSSID"
    ENCRYPTION_KEY="暗号化キー"
    NTP_SERVER="NTPサーバのアドレス"
    URL="取得したいRSSのURLなど"
    -----------------------------------------------
"""
import daichamame_ssd1306
import daichamame_net
import sample_font
import env # ssid ,encryption_key,ntp server,rss url 


# wifi接続　2.4 GHzの802.11 b/g/nに対応
wifi = daichamame_net.net()
wifi.connect_to_wifi(ssid=env.SSID,encryption_key=env.ENCRYPTION_KEY)

# RTCの初期値にNTPサーバから取得した時刻をJSTで登録
wifi.set_time_jst(env.NTP_SERVER)
rtc = machine.RTC()
# http リクエストサンプル
url=env.URL
# httpリクエストの結果をファイル出力する関数
wifi.https_request_to_file(url,max_size=8192,filename="rss.xml")
# httpリクエストの結果をメモリで返す関数
buf=wifi.https_request(url,max_size=1024)
print(buf) # 取得したデータを出力してみる

# 画面表示
# SSD1306とはSDA=GP4,SCL=GP5を使用したI2C通信
ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=sample_font.fonta16,font_size=16)
ssd1306.init()  # デバイスの初期処理
ssd1306.clear() # 画面の消去
ssd1306.flash() # フラッシュ画面

#　初回1回表示
ctime=rtc.datetime() # 現在時刻を取得
ssd1306.print(0,0,"{:4d}年{:2d}月{:2d}日".format(ctime[0],ctime[1],ctime[2]),1)  # 文字を描く
ssd1306.print(32,16,"{:2d}:{:02d}".format(ctime[4],ctime[5]),2)  # 文字を描く
ssd1306.display()    # 画面を表示する
        
# 時計表示処理
while True:
    ctime=rtc.datetime() # 現在時刻を取得
    if ctime[6] == 0: # 1分間に1回（秒が0になった時)表示更新
        ssd1306.print(0,0,"{:4d}年{:2d}月{:2d}日".format(ctime[0],ctime[1],ctime[2]),1)  # 文字を描く
        ssd1306.print(32,16,"{:2d}:{:02d}".format(ctime[4],ctime[5]),2)  # 文字を描く
        ssd1306.display()    # 画面を表示する

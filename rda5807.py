import daichamame_rda5807
import time

# RDA5807の初期化
radio = daichamame_rda5807.RDA5807(id=0,scl_pin=5,sda_pin=4)
# FMラジオの起動
radio.init()

# レジスタの値をチェックしてラジオ局を探す
print("ラジオ局検索開始(76MHz - 108MHz)")
for i in range(760 ,1080):
    f = i/10
    radio.set_freq(f)
    # 判定するための時間を調整
    time.sleep_ms(200)
    ret=radio.check_station() # ラジオ局の判定
    if(ret):
        # 見つけたら表示
        print(str(f) + " : ラジオ局を見つけました。" )
print("ラジオ局検索終了")

# ボリュームを設定(0 - 15)
radio.set_volume(10)
# 周波数の設定(76.0-108.0)
sel_ch = input("チャンネルを指定してください(76.0-108.0)")
radio.set_freq(float(sel_ch))


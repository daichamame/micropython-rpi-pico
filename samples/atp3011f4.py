"""ATP3011F4 sample"""

import daichamame_atp3011f4   
import time

atp=daichamame_atp3011f4.ATP3011F4()

# チャイム
atp.chime(0)
atp.chime(1)

atp.send_cmd("sanpuru.puroguramu.desu")
time.sleep_ms(1000)
# 日付
atp.talk_date(2024,3,2)
time.sleep_ms(1000)
# 時刻
atp.talk_time(5,12)
time.sleep_ms(1000)
# 気温と湿度
atp.talk_temp(16.5,40)
time.sleep_ms(1000)
# コード番号
atp.talk_code("ATP3011F4")
time.sleep_ms(1000)
# 金額
atp.talk_amount(123456)
time.sleep_ms(1000)
# 電話番号
atp.talk_telno("12340-56789-01234")
time.sleep_ms(1000)






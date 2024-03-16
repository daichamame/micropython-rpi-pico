""" ssd1306 に温湿度を表示してはなす"""

import daichamame_ssd1306
import daichamame_dht20
import daichamame_atp3011f4  
import sample_font

atp=daichamame_atp3011f4.ATP3011F4()
dht20 = daichamame_dht20.DHT20()
dht20.init()
ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=sample_font.fonta16,font_size=16)
ssd1306.init()
ssd1306.clear()
# 初回表示
(temp,hum)=dht20.get_data()
ssd1306.print(0,0,"温度"+str(int(temp))+"℃",1)
ssd1306.print(0,16,"湿度"+str(int(hum))+"％",1)
ssd1306.display()
atp.talk_temp(int(temp),int(hum))

    

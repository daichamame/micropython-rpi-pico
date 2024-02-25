import daichamame_aqm1602
import time

aqm=daichamame_aqm1602.AQM1602()
aqm.init()
aqm.hello()
time.sleep(3)
aqm.clear()
aqm.print(1,"MicroPython")
aqm.print(2,"ﾗｽﾞﾊﾟｲ ﾋﾟｺ")
    
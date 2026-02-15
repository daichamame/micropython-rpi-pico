"""SSD1306 sample"""

import daichamame_ssd1306
import sample_font
import math
import time


ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=sample_font.fonta16,font_size=16)
ssd1306.init()  # デバイスの初期処理
ssd1306.clear() # 画面の消去
ssd1306.flash() # フラッシュ画面

# ローテーションデモ
for x in range(4):
    ssd1306.set_rotate(x*90)    # 画面の回転
    ssd1306.clear()
    ssd1306.print(0,0,"2024年",1)  # 文字を描く
    ssd1306.print(0,16,"2月25日",1)
    ssd1306.rect(0,32,16,16,1,0)
    ssd1306.rect(16,48,16,16,1,1)
    ssd1306.rect(32,32,16,16,1,0)
    ssd1306.rect(48,48,16,16,1,1)
    ssd1306.display()           # 画面を表示する
    time.sleep(1)

ssd1306.set_rotate(0)
ssd1306.clear()
#　書き換えデモ
ssd1306.print(0,0,"2024年2月25日",1)
ssd1306.print(0,16,"0123456789",1)

for d in range(64):
    ssd1306.partial_buffer_clear(0,32,128,32) # 指定した範囲のバッファを初期化
    for x in range(128):
        y=48+int(math.sin(math.pi*(x+d*2)/32)*16)   # Y座標の計算
        ssd1306.pset(x,y,1)                         # 点を描く
        y=48+int(math.cos(math.pi*(x+d*4)/32)*16)
        ssd1306.pset(x,y,1)
    ssd1306.display()           # 画面を表示する
    

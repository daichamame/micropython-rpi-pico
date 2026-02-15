"""
   Waveshare Pico LCD-1.3をMicroPythonで動かす
   Raspberry pi picoに以下のファイルを設置

   /lib/daichamame_picolcd13.py
     Pico LCD 1.3 の操作用モジュール
   /lib/sample_font.py
   /img/sample.bmp
     デモ用ビットマップファイル(16ビットカラー)
"""
import sample_font
import daichamame_picolcd13
import time
import random
import math
from machine import Pin,SPI

# 16x16のアイコン
icon32=(
[0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0C00,0x0188,0x0C00,0x0308,0x1E00,0x061C,0x1300,0x1E1C,0x3180,0x3C38,0x60C0,0x3878,0xE070,0x30F1,0x8038,0x31E3,0x001C,0x3387,0x1F8C,0x3F06,0x1F80,0x1E00,0x0000,0x3800,0x03F0,0x7080,0x7FF0,0xF0E0,0xFFF0,0xE078,0x1800,0xCFF8,0x1800,0xFFF8,0x3000,0xE608,0x61C0,0x0640,0xC0E0,0x4661,0x83F0,0x6E61,0x8FF8,0x6E61,0xBFB8,0x6E61,0xFC18,0x6601,0xC018,0x0701,0xC018,0x0600,0x0000,0x0000,0x0000,0x0000,0x0000],
[0x0000,0x0000,0x0090,0x0000,0x0891,0x0000,0x0492,0x0000,0x0204,0x0000,0x18F1,0x8000,0x05FA,0x0000,0x03FC,0x0000,0x3BFD,0xC000,0x03FC,0x0000,0x01F8,0xF800,0x08F3,0xFE00,0x1207,0xFF00,0x220F,0xFFC0,0x04FF,0xFFE0,0x03FF,0xFFE0,0x07FF,0xFFF0,0x0FFF,0xFFF0,0x1FFF,0xFFF0,0x3FFF,0xFFE0,0x1FFF,0xFFE0,0x1FFF,0xFFC0,0x0FFE,0xFF80,0x07FC,0x0040,0x0800,0x1240,0x0924,0x9240,0x0924,0x9200,0x0924,0x9040,0x0124,0x9240,0x0904,0x8240,0x0104,0x1240,0x0000,0x0000],
[0x0000,0x0000,0x000F,0xF800,0x0000,0x8000,0x01FF,0xFFC0,0x0100,0x8040,0x017E,0xBF40,0x0000,0x8000,0x007E,0xBF00,0x0000,0x0000,0x007F,0xFF00,0x0000,0x0100,0x007F,0xFF00,0x0000,0x0100,0x007F,0xFF00,0x0000,0x0000,0x0000,0x0030,0x0001,0xE030,0x0307,0xF800,0x030F,0xFC00,0x000D,0xEC00,0x000D,0xEC0C,0x006F,0xFC0C,0x0067,0xF980,0x0003,0xF180,0x1807,0xF800,0x180F,0xFC18,0x019F,0xFE18,0x019F,0xFE00,0x001F,0xFE00,0x001F,0xFE00,0x000F,0xFC00,0x0007,0xF800],
)
last_trig_time = 0
# キーを押されたときに実行される関数
def button_pressed_action(p):
    # 押されたキー情報を出力する
    global last_trig_time
    current_time = time.ticks_ms()
    if current_time - last_trig_time > 300:  # 300ms間隔（連続処理防止用）
        last_trig_time = current_time
        print(f"ﾎﾞﾀﾝｶﾞｵｻﾚﾏｼﾀ{p}")
        
# LCD初期化
lcd=daichamame_picolcd13.PICOLCD13(font_array=sample_font.fonta16,font_size=16,rotate=90)
# 一面塗りつぶし処理(8回）
start_time = time.ticks_ms()
lcd.clear(0x0000ff)
lcd.clear(0x00ff00)
lcd.clear(0x00ffff)
lcd.clear(0xff0000)
lcd.clear(0xff00ff)
lcd.clear(0xffff00)
lcd.clear(0xffffff)
lcd.clear()
end_time = time.ticks_ms()
elapsed_time = time.ticks_diff(end_time, start_time)/8
print(f"1回あたりの塗りつぶし処理時間: {elapsed_time} ミリ秒")

#画像表示
start_time = time.ticks_ms()
lcd.draw_bitmap('/img/sample.bmp')
end_time = time.ticks_ms()
elapsed_time = time.ticks_diff(end_time, start_time)
print(f"16bitビットマップ表示処理時間: {elapsed_time} ミリ秒")
time.sleep(3)
lcd.clear()

# 線形描画
start_time = time.ticks_ms()
for x  in range(0,240,40):
    lcd.line(0,0,240-x,240,x << 16 |(0xff-x) << 8 |0xa0)
    lcd.line(240,240,x,0,x << 16 |(0xff-x) << 8 |0xa0)
for y  in range(0,240,40):
    lcd.line(0,0,240,240-y,y << 16 |(0xff-y) << 8 |0xa0)
    lcd.line(240,240,0,y,y << 16 |(0xff-y) << 8 |0xa0)
time.sleep(3)
lcd.clear()
# 曲線描画
for d in range(0,240,20):
    for x in range(0,240):
        y=240+int(math.sin(math.pi*(x+d)*2/90)*8)-d   # Y座標の計算
        lcd.pset(int(x), int(y), (0xff - x) << 16 |x << 8 |y)
end_time = time.ticks_ms()
elapsed_time = time.ticks_diff(end_time, start_time)
print(f"図形描画処理時間: {elapsed_time} ミリ秒")
time.sleep(3)
lcd.clear()

# 文字表示処理
start_time = time.ticks_ms()
lcd.print( 0,  0,"2025年",0xa0f0e0,ratio=3)
lcd.print(24, 50," 5月26日",0xf0a0e0,ratio=3)
lcd.print(24,100,"12:34:56",0xa0e0f0,ratio=3)
for i in range(3): 
    lcd.draw_icon(i*64,160,icon32[i],0x00ff88,32)            
end_time = time.ticks_ms()
elapsed_time = time.ticks_diff(end_time, start_time)
print(f"文字表示処理時間: {elapsed_time} ミリ秒")
time.sleep(3)
# ランダムに四角形を表示
start_time = time.ticks_ms()
for i in range(300):
    sx=random.randint(0,220)
    sy=random.randint(0,220)
    w=random.randint(10,30)
    h=random.randint(10,30)
    r=random.randint(128,255)
    g=random.randint(128,255)
    b=random.randint(128,255)
    lcd.rect(sx,sy,w,h, r << 16 | g << 8 | b)
end_time = time.ticks_ms()
elapsed_time = time.ticks_diff(end_time, start_time)
print(f"300個の四角形表示処理時間: {elapsed_time} ミリ秒")

# 向きを変更して一部スクロール表示とボタン押下の処理
lcd=daichamame_picolcd13.PICOLCD13(font_array=sample_font.fonta16,font_size=16,rotate=0)
# ボタンが押されたら、button_pressed_action関数を実行する割り込み設定
lcd.key_a.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.key_b.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.key_x.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.key_y.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.joy_u.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.joy_d.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.joy_l.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.joy_r.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.joy_c.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed_action)
lcd.clear()

# 文字表示処理
start_time = time.ticks_ms()
lcd.print( 0,  0,"2025年",0xa0f0e0,ratio=3)
lcd.print(24, 60," 5月26日",0xf0a0e0,ratio=3)
# 以下はスクロールする領域
lcd.print(20,180,"気温:23℃",0xf000f0)
lcd.print(20,220,"湿度:45％",0xf0f000)
lcd.draw_icon(50,260,icon32[1],0x00ff88,32)
end_time = time.ticks_ms()
elapsed_time = time.ticks_diff(end_time, start_time)
print(f"文字表示処理時間: {elapsed_time} ミリ秒")

position=128 #　スクロールを開始する位置
i=0 # 変化量
#　画面スクロール
lcd.set_scroll(position,320-position,0) # スクロール設定(0からposition までが固定、positionから320までがスクロール範囲)

# スクロール処理1
# スクロールをさせて高さ240から320の位置を表示させる
while True:
    if i < 320-position:
        lcd.scroll(position+i)
        i=i+1
    else:
        break
    time.sleep_ms(40) # 速度調整

lcd.rect(0,position,240,320-position,0x000000)
bottom=1
count=0
# スクロール処理2
# 下の非表示領域に文字を出力後、表示させるデモ
# 100までカウントする
while True:
    if i < 320-position:
        lcd.scroll(position+i)
        i=i+1
        # 非表示位置の計算
        bottom=position + (i + (240-position)) % (320 - position) # 表示
    else:
        i=0
    if bottom % 32 == 0:
        if count < 100:
            count=count+1
            lcd.print(100,bottom,"{:03}".format(count),0xf0f000)
        else:
            break


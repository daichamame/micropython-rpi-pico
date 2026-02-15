"""
　　このプログラムは、
    ILI9341搭載2.8インチSPI制御タッチパネル付TFT液晶 MSP2807を
    Raspberry pi picoのMicroPythonを使用して制御しています。
    特に、SPI0をSDカードとタッチパネルの制御用に使用しており、
    共用したときの使い方のサンプルとなっています。
    
    動作はSDカードに保存された画像（bmpファイル）を読み取り表示し、
    タッチパネルを使用して画像を切り替えることができます。

    〇Raspberry Pi Picoに設置するファイル
    
    ili9341_sd.py このファイル
    /lib/daichamame_ili9341.py
    /lib/fontloader.py
    別途用意するフォントファイル：
    /font/shnm8x16r.bdf		東雲フォントのshnm8x16r.bdf

    〇SDカードに320x240サイズのビットマップファイル以下のように用意
    /img/sample_1.bmp
    /img/sample_2.bmp
    /img/sample_3.bmp
    

"""
import daichamame_ili9341
import fontloader
from machine import Pin, SPI
import sdcard
import os

# メイン
if __name__ == "__main__":
    # /font/フォルダに 東雲フォントのshnm8x16r.bdfを表示用に利用
    fnt=fontloader.FontLoader("/font/shnm8x16r.bdf")
    shnmfont=fnt.load_font() # フォントデータを読み込む       
    lcd=daichamame_ili9341.ili9341(font_array=shnmfont,font_size=16,rotate=270)
    lcd.clear()

    lcd.t_cs(1)

    # SDカード用SPIの初期化（SPI0使用）
    # SD_CS 5、SD_MOSI 3、SD_MISO 4、SD_SCK 2
    # SPI0をタッチパネルと共用して使用します。
    spi_sd = SPI(0, baudrate=2000000, polarity=0, phase=0,sck=Pin(2), mosi=Pin(3), miso=Pin(4))
    cs = Pin(5, Pin.OUT)

    # SDカードの初期化とマウント
    sd = sdcard.SDCard(spi_sd, cs)
    os.mount(sd, "/sd")
    total = sd.sectors * 512  # バイト単位
    print("SDカードの容量: {:.2f} MB".format(total / (1024 * 1024)))
    print('----------------------------------------------------------------------')
    stat = os.statvfs("/sd/")
    size = stat[1] * stat[2] /1024 /1024
    free = stat[0] * stat[3] /1024 /1024
    used = size - free
    print("Size : {:,} MB".format(size))
    print("Used : {:,} MB".format(used))
    print("Free : {:,} MB".format(free))
    # 初期画像表示
    img_count=1
    lcd.draw_bitmap('/sd/img/sample_1.bmp')
    # SPI0をSDカードからタッチパネルへ切り替え
    cs.value(1)
    lcd.t_cs(0)
    # 画像表示とボタン描画
    lcd.add_button(  0,200, 80, 40," << ",0xffffff,0x33b6cc)
    lcd.add_button(240,200, 80, 40," >> ",0xffffff,0x33b6cc)

    while 1:
        if lcd.touch_flag == True:
            (status,x,y,hit)=lcd.read_touch_position()
            if status == True and len(hit)>0:
                if hit[0] == 0:
                    img_count=(img_count - 1)*(img_count > 1) + 3*(img_count == 1)
                elif hit[0] == 1:
                    img_count=(img_count + 1)*(img_count < 3) + (img_count == 3)
                # SPI0をタッチパネルからSDカードへ切り替え
                lcd.t_cs(1)
                # 読み込み画像ファイル名
                filename = "/sd/img/sample_" + str(img_count) + ".bmp"
                lcd.clear()
                # 画像表示とボタン描画
                lcd.draw_bitmap(filename)
                lcd.add_button(  0,200, 80, 40," << ",0xffffff,0x33b6cc)
                lcd.add_button(240,200, 80, 40," >> ",0xffffff,0x33b6cc)
                # SPI0をSDカードからタッチパネルへ切り替え
                cs.value(1)
                lcd.t_cs(0)
                lcd.touch_flag = False

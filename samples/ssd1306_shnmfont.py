"""
SSD1306 の表示に東雲フォント（JIS X 0201）を使用した例

接続：
  SSD1306は、I2C CH:0 SDA=GP4,SCL=GP5,FREQ=400kHz

"""

import daichamame_ssd1306
import fontloader
import time
import micropython

print("フォントを読み込む前のメモリ")
micropython.mem_info()
# 例：/font/フォルダに 東雲フォントのshnm8x16r.bdfを配置した場合、以下のように記述します
fnt=fontloader.FontLoader("/font/shnm8x16r.bdf")
shnmfont=fnt.load_font()
print("フォントを読み込み後のメモリ")
micropython.mem_info()
# font_size で、読み込んだフォントのサイズを設定
ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=shnmfont,font_size=16)
ssd1306.init()  # デバイスの初期処理
ssd1306.clear() # 画面の消去
ssd1306.flash() # フラッシュ画面

ssd1306.clear() # 画面の消去
ssd1306.print_half(0, 0," !\"#$%&7()*+,-./",1)
ssd1306.print_half(0,16,"0123456789:;<=>?",1)
ssd1306.print_half(0,32,"@ABCDEFGHIJKLMNO",1)
ssd1306.print_half(0,48,"PQRSTUVWXYZ[\]^_",1)
ssd1306.display()           # 画面を表示する
time.sleep_ms(5000)
ssd1306.clear() # 画面の消去
ssd1306.print_half(0, 0,"`abcdefghijklmno",1)
ssd1306.print_half(0,16,"pqrstuvwxyz{|}~",1)
ssd1306.print_half(0,32,"｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰ",1)
ssd1306.print_half(0,48,"ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ",1)
ssd1306.display()           # 画面を表示する
time.sleep_ms(5000)
ssd1306.clear() # 画面の消去
ssd1306.print_half(0, 0,"ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ",1)
ssd1306.print_half(0,16,"ﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓ",1)
ssd1306.print_half(0,32,"ﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝﾞﾟ",1)
ssd1306.print_half(0,48,"",1)
ssd1306.display()           # 画面を表示する
   

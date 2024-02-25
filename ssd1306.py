"""SSD1306 sample"""

import daichamame_ssd1306
import sample_font

ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=sample_font.fonta16,font_size=16)
ssd1306.init()
ssd1306.clear()
ssd1306.flash()
ssd1306.print(0,0,"1234567890:",1)
ssd1306.print(0,32,"2024年2月25日",1)
ssd1306.display()



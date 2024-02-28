"""EPD266 e-Paper module. sample"""

import daichamame_epd266
import sample_font

epd = daichamame_epd266.Epd266(rotate=90,font_array=sample_font.fonta16,font_size=16)

epd.init()
epd.clear()
epd.buffer_clear()
epd.print(0,0,"2024年2月2日",1)
epd.print(0,16,"2024年2月2日",2)
epd.print(0,48,"2024年2月2日",3)
epd.print(0,96,"12:34:56",2)
epd.print(0,128,"12:34:56",1)
epd.display()

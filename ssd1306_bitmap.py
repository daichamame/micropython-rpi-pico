"""SSD1306 sample"""

import daichamame_ssd1306
import micropython
testfont=(
[0x00    ,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], # 空白
[0x32    ,0x00,0x18,0x24,0x42,0x42,0x02,0x02,0x02,0x0C,0x10,0x20,0x40,0x42,0x7E,0x00,0x00], #2
[0x33    ,0x00,0x18,0x24,0x42,0x42,0x02,0x04,0x18,0x04,0x02,0x42,0x42,0x24,0x18,0x00,0x00], #3
[0xE28483,0x0000,0x3000,0x4BF0,0x4C08,0x3408,0x0808,0x0800,0x0800,0x0800,0x0800,0x0800,0x0808,0x0408,0x0408,0x03F0,0x0000],#℃
[0xE6B097,0x0000,0x0800,0x0FF8,0x1000,0x2FF8,0x0000,0x1FF8,0x0008,0x0028,0x0448,0x0288,0x0108,0x0288,0x0448,0x1806,0x0000],#気
[0xE6B8A9,0x0000,0x0000,0x01F8,0x3908,0x0108,0x01F8,0x0108,0x0108,0x39F8,0x0000,0x03FC,0x0294,0x0A94,0x1294,0x27FE,0x0000],#温
)
# 32x32 icon データ
icon=(
[0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0C00,0x0188,0x0C00,0x0308,0x1E00,0x061C,0x1300,0x1E1C,0x3180,0x3C38,0x60C0,0x3878,0xE070,0x30F1,0x8038,0x31E3,0x001C,0x3387,0x1F8C,0x3F06,0x1F80,0x1E00,0x0000,0x3800,0x03F0,0x7080,0x7FF0,0xF0E0,0xFFF0,0xE078,0x1800,0xCFF8,0x1800,0xFFF8,0x3000,0xE608,0x61C0,0x0640,0xC0E0,0x4661,0x83F0,0x6E61,0x8FF8,0x6E61,0xBFB8,0x6E61,0xFC18,0x6601,0xC018,0x0701,0xC018,0x0600,0x0000,0x0000,0x0000,0x0000,0x0000],
[0x0000,0x0000,0x0090,0x0000,0x0891,0x0000,0x0492,0x0000,0x0204,0x0000,0x18F1,0x8000,0x05FA,0x0000,0x03FC,0x0000,0x3BFD,0xC000,0x03FC,0x0000,0x01F8,0xF800,0x08F3,0xFE00,0x1207,0xFF00,0x220F,0xFFC0,0x04FF,0xFFE0,0x03FF,0xFFE0,0x07FF,0xFFF0,0x0FFF,0xFFF0,0x1FFF,0xFFF0,0x3FFF,0xFFE0,0x1FFF,0xFFE0,0x1FFF,0xFFC0,0x0FFE,0xFF80,0x07FC,0x0040,0x0800,0x1240,0x0924,0x9240,0x0924,0x9200,0x0924,0x9040,0x0124,0x9240,0x0904,0x8240,0x0104,0x1240,0x0000,0x0000],
[0x0000,0x0000,0x000F,0xF800,0x0000,0x8000,0x01FF,0xFFC0,0x0100,0x8040,0x017E,0xBF40,0x0000,0x8000,0x007E,0xBF00,0x0000,0x0000,0x007F,0xFF00,0x0000,0x0100,0x007F,0xFF00,0x0000,0x0100,0x007F,0xFF00,0x0000,0x0000,0x0000,0x0030,0x0001,0xE030,0x0307,0xF800,0x030F,0xFC00,0x000D,0xEC00,0x000D,0xEC0C,0x006F,0xFC0C,0x0067,0xF980,0x0003,0xF180,0x1807,0xF800,0x180F,0xFC18,0x019F,0xFE18,0x019F,0xFE00,0x001F,0xFE00,0x001F,0xFE00,0x000F,0xFC00,0x0007,0xF800],
)

ssd1306 = daichamame_ssd1306.SSD1306(rotate=0,font_array=testfont,font_size=16)
ssd1306.init()
ssd1306.clear()
ssd1306.flash()
ssd1306.print(0,0,"気温",1)
ssd1306.print(0,16,"23 ℃",1)
ssd1306.draw_icon(0,32,icon[0],1)
ssd1306.draw_icon(32,32,icon[1],1)
ssd1306.draw_icon(64,0,icon[2],2)
ssd1306.display()



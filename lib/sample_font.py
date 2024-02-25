# Excelで作成してみたフォントサンプル
# 各行の先頭は、文字コードで、１文字は、文字コード＋ビットマップ情報となっています。
# 並び順は、文字コードでソートしています。
fonta16=(
[0x00    ,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], # 空白 
[0x30    ,0x00,0x18,0x24,0x24,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x24,0x24,0x18,0x00,0x00], #0
[0x31    ,0x00,0x18,0x28,0x48,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x00,0x00], #1
[0x32    ,0x00,0x18,0x24,0x42,0x42,0x02,0x02,0x02,0x0C,0x10,0x20,0x40,0x42,0x7E,0x00,0x00], #2
[0x33    ,0x00,0x18,0x24,0x42,0x42,0x02,0x04,0x18,0x04,0x02,0x42,0x42,0x24,0x18,0x00,0x00], #3
[0x34    ,0x00,0x04,0x44,0x44,0x44,0x44,0x44,0x44,0x44,0x44,0x7E,0x04,0x04,0x04,0x00,0x00], #4
[0x35    ,0x00,0x7E,0x40,0x40,0x40,0x40,0x58,0x64,0x02,0x02,0x02,0x42,0x42,0x3C,0x00,0x00], #5
[0x36    ,0x00,0x3C,0x62,0x42,0x40,0x58,0x64,0x42,0x42,0x42,0x42,0x42,0x42,0x3C,0x00,0x00], #6
[0x37    ,0x00,0x7E,0x42,0x42,0x02,0x02,0x04,0x04,0x04,0x04,0x08,0x08,0x08,0x08,0x00,0x00], #7
[0x38    ,0x00,0x18,0x24,0x42,0x42,0x42,0x24,0x18,0x24,0x42,0x42,0x42,0x24,0x18,0x00,0x00], #8
[0x39    ,0x00,0x3C,0x42,0x42,0x42,0x42,0x42,0x42,0x3E,0x02,0x42,0x42,0x42,0x3C,0x00,0x00], #9
[0x3A    ,0x00,0x00,0x00,0x00,0x18,0x18,0x00,0x00,0x00,0x00,0x18,0x18,0x00,0x00,0x00,0x00], #:
[0xE5B9B4,0x0000,0x0800,0x1FFC,0x2080,0x4080,0x0080,0x1FFC,0x1080,0x1080,0x1080,0x7FFC,0x0080,0x0080,0x0080,0x0080,0x0000], # 年
[0xE697A5,0x0000,0x0000,0x0FF8,0x0808,0x0808,0x0808,0x0808,0x0FF8,0x0808,0x0808,0x0808,0x0808,0x0808,0x0FF8,0x0000,0x0000], # 日
[0xE69C88,0x0000,0x0000,0x07F8,0x0408,0x0408,0x07F8,0x0408,0x0408,0x07F8,0x0408,0x0408,0x0808,0x0808,0x1008,0x1038,0x0000], # 月
)
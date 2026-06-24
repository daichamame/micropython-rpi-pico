"""
EPD266 e-Paper module sample

このサンプルは、以下の 2 つのデモを行います。

1. 電子ペーパーへの文字表示デモ
   - 日付や時刻を複数サイズのフォントで描画します。

2. WireFrame（簡易 3D ライン描画）のデモ
   - 2 種類のワイヤーフレーム図形を生成し、
     電子ペーパー上に左右に並べて描画します。
   - メモリ使用量を抑えるため、WireFrame インスタンスと
     計算結果は描画後に破棄し、gc.collect() を実行しています。

このサンプルは、EPD266 モジュールの基本的な使い方と、
WireFrame 描画の応用例を示すためのものです。

インストール
/lib/daichamame_epd266.py
/lib/sample_font.py
/lib/util/daichamame_wireframe.py
epd266.py

"""
import daichamame_epd266
import sample_font
import util.daichamame_wireframe
import gc
import time

# 電子ペーパーの初期化処理
epd = daichamame_epd266.Epd266(rotate=270,font_array=sample_font.fonta16,font_size=16)
epd.init()
epd.clear()
epd.buffer_clear()
# 日付表示デモ（サイズ違い）
epd.print(0,0,"2024年2月2日",1)  
epd.print(0,16,"2024年2月2日",2)
epd.print(0,48,"2024年2月2日",3)
epd.print(0,96,"12:34:56",2)
epd.print(0,128,"12:34:56",1)
epd.display()
time.sleep(3) # 3秒スリープ
epd.clear()
epd.buffer_clear()
# 1つめのワイヤーフレーム図形を作成
epd.print(100,136,"2026年6月22日 12:34:56",1,bold=1)  
cx=80
cy=70
wf=util.daichamame_wireframe.WireFrame(4,50,40,0) 
(w,h,bmp)=wf.project(0.2,0.3,0.4)
for j in range(h):
    for i in range(w-1):
        x1, y1, c1 = bmp[j][i]
        x2, y2, c2 = bmp[j][i+1]
        epd.line(int(x1)+cx, int(y1)+cy,int(x2)+cx, int(y2)+cy)
for j in range(h-1):
    for i in range(w):
        x1, y1, c1 = bmp[j][i]
        x2, y2, c2 = bmp[j+1][i]
        epd.line(int(x1)+cx, int(y1)+cy,int(x2)+cx, int(y2)+cy)
# インスタンスと、計算結果を破棄
wf = None
bmp = None
gc.collect()
# 2つめのワイヤーフレーム図形を作成
cx=200
cy=70
wf=util.daichamame_wireframe.WireFrame(4,50,40,1)
(w,h,bmp)=wf.project(0.2,0.3,0.4)
for j in range(h):
    for i in range(w-1):
        x1, y1, c1 = bmp[j][i]
        x2, y2, c2 = bmp[j][i+1]
        epd.line(int(x1)+cx, int(y1)+cy,int(x2)+cx, int(y2)+cy)
for j in range(h-1):
    for i in range(w):
        x1, y1, c1 = bmp[j][i]
        x2, y2, c2 = bmp[j+1][i]
        epd.line(int(x1)+cx, int(y1)+cy,int(x2)+cx, int(y2)+cy)
epd.display()


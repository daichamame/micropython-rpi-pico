"""
ST7789V ディスプレイ表示サンプル
 
本サンプルは以下の機能をまとめて確認するためのデモです：
  - ST7789V ドライバ（daichamame_st7789）による文字描画
  - BDF フォント読み込み（fontloader）
  - WireFrame モジュールを用いた簡易 3D ワイヤーフレーム描画
  - スクロール領域の設定とスクロールアニメーション
  - 画面の明るさフェード（バックライト PWM 制御）

依存モジュール：
  daichamame_st7789        : ST7789V 用描画ドライバ
  util.daichamame_wireframe: ワイヤーフレーム生成ユーティリティ
  fontloader               : BDF フォントローダー

動作概要：
  1. フォントを読み込み、LCD を初期化
  2. タイトル文字列を描画
  3. ワイヤーフレームを投影し、線画として描画
  4. 画面下部をスクロールさせるアニメーションを実行
  5. 最後にバックライトを段階的にフェード
"""
import daichamame_st7789
import util.daichamame_wireframe
import time
import fontloader

# フォント読み込み
fnt=fontloader.FontLoader("/font/shnm8x16r.bdf") # 東雲フォントのBDFファイルを読み込み
shnmfont=fnt.load_font()
# LCD初期化（回転なし、明るさ65535)
lcd=daichamame_st7789.ST7789V(font_array=shnmfont,font_size=16,rotate=0)

# 画面消去
lcd.clear()

# 文字を2倍の大きさで表示
lcd.print(0,0,"ST7789V ｻﾝﾌﾟﾙ",0xffffff,ratio=2)

# ワイヤー画像描画
cx=120 # ワイヤーフレームの描画中心 X
cy=140 # ワイヤーフレームの描画中心 Y
wf=util.daichamame_wireframe.WireFrame(5,80,40,1) # ワイヤーフレームデータの初期化
(w,h,bmp)=wf.project(0.4,0.3,0.4) # (幅, 高さ, 投影結果の2次元配列)
# 投影データの表示
for j in range(h): 
    for i in range(w-1):
       x1, y1, c1 = bmp[j][i]
       x2, y2, c2 = bmp[j][i+1]
       lcd.line(int(x1)+cx, int(y1)+cy,int(x2)+cx, int(y2)+cy,c1)
for j in range(h-1):
    for i in range(w):
        x1, y1, c1 = bmp[j][i]
        x2, y2, c2 = bmp[j+1][i]
        lcd.line(int(x1)+cx, int(y1)+cy,int(x2)+cx, int(y2)+cy,c1)

# スクロール
# 文字表示部分を固定して、スクロール
pos=32
lcd.set_scroll(pos,320-pos,0)
for i in range(320-pos):
    lcd.scroll(pos+i)
    time.sleep_ms(10) # 速度調整

# 画面の明るさを段階的に変更
lcd.fade_to(1000)  # 段階的に暗くする
time.sleep_ms(500) 
lcd.fade_to(65535) # 段階的に明るくする

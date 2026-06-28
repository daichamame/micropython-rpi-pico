# MicroPython Pico LCD 1.3 for Raspberry Pi Pico  
**Waveshare Pico LCD 1.3向け 実装ガイド**

このモジュールは、Raspberry Pi Pico と Pico LCD 1.3 を動作させるための軽量 MicroPython ドライバです。  
---

## 1. 対応デバイス
- Raspberry Pi Pico / Pico W  
- Waveshare Pico LCD 1.3
- MicroPython  

---

## 2. モジュールの特徴
- 基本描画（線、四角形、アイコン、ビットマップ）  
- 日本語テキスト描画対応（外部フォント方式 / 東雲フォントなど） 
- 表示領域は240x240ですが、メモリは240x320保持しているため、スクロールさせ240-320の部分を表示可能
- 16ビットと24ビットのbitmap画像表示

---

## 3. インストール
```
/lib/daichamame_picolcd13.py
/fonts/（外部取得フォント）
```

---

## 4. 使い方（基本）

### 4.1 初期化例(東雲フォントのBDFファイルを読み込み例)
```python
import daichamame_picolcd13
import fontloader
fnt=fontloader.FontLoader("/font/shnm8x16r.bdf") # 東雲フォントのBDFファイルを読み込む
shnmfont=fnt.load_font()
lcd = daichamame_picolcd13.PICOLCD13(rotate=90,font_array=shnmfont,font_size=16)

```

---

### 4.2 描画例
```python
lcd.clear(0x000000) # 指定色で描画
lcd.print(0,0,"Pico LCD ｻﾝﾌﾟﾙ",0xffffff) # テキスト描画
lcd.line(50, 50,100,100,0xffffff) # 線描画
lcd.rect(100,100,80,40,0xcccc00) # 四角形描画
```

---

## 5. API リファレンス
- `reset()	# HWリセット`
- `sw_reset()	# SWリセット`
- `sleep_in() # スリープ イン`
- `sleep_out() # スリープ アウト`
- `init_scroll() # スクロール設定の初期化`
- `set_scroll(tfa,vsa,bfa) # スクロールエリア定義`
- `scroll(num) # スクロール`
- `clear(color) # 指定色で初期化`
- `display_off() # ディスプレイオフ`
- `display_on() # ディスプレイオン`
- `print(x,y,buf,color,bgcolor,ratio,bold) # 文字を表示`
- `line(sx,sy,ex,ey,color) # 線を描く`
- `rect(x,y,width,height,color) # 四角形を描く`
- `draw_icon(x,y,buf,color,size,bgcolor,ratio) # アイコン(32x32 or 16x16)を描く`
- `draw_bitmap(file) # ビットマップ画像ファイルを表示`
- `get_lastkey() # ジョイスティック、ボタンの最新値取得`

---

## 6. 使用例
### 日本語フォント（16ドット・3倍角）とアイコン描画（32ドット・2倍角）
![pico lcd](../img/picolcd_2.png)<br>
16ドットのフォントを外部ファイルとして読み込み倍率を変えて表示した例です。<br>
32x32ドットのアイコンを倍率を変えて表示した例
### スクロール
![pico lcd](../img/picolcd_3.png)
![pico lcd](../img/picolcd_4.png)<br>
下半分をスクロールしています。この向きで使用すると幅が240ピクセル、高さが320ピクセルとなります。
## 7. ライセンス
MIT License  


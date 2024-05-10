# MicroPythonで作成したサンプル集
Raspberry Pi Pico でMicroPythonを使って動作確認をするために作成したプログラムを整理したものです。

## ディスプレイ

主に日本語を表示させたいという理由で作成しています。

### AQM1602
カタカナ表示に対応しました。<br>


![aqm1602](img/aqm1602_1.png)

### OLED SSD1306
フォントの情報を配列に持たせて簡易的に日本語を表示させる仕組みで実装しています。<br>
配列に持たせることでRAMを利用する為、多くのフォント情報は持てませんが、決まった単語を表示する用途などで利用できると思います。

![ssd1306](img/ssd1306_0.png)

12ドットと16ドットのフォントを別途、用意して表示させた例です。<br>

![ssd1306](img/ssd1306_1.png)


アイコンを表示した例です。(ssd1306_bitmap.py)

![ssd1306](img/ssd1306_2.png)


アイコンの作成は、PythonのKivyで作成したツールを使用しています。

[ドット絵つくる(https://github.com/daichamame/kv-dot_e_maker)](https://github.com/daichamame/kv-dot_e_maker)


### Waveshare 2.66inch E-Paper
SSD1306のモジュールと同様です。<br>
簡易的に日本語を表示させる仕組みで実装しています。<br>
16ドット、2倍角、3倍角の大きさで表示しています。

![epd266](img/epd266_1.png)


16ドットのフォントを別途、用意して表示させた例です。

![epd266](img/epd266_2.png)

アイコンを表示した例です。

![epd266](img/epd266_3.png)

## 音声合成LSI
### ATP3011F4-PU

接続方法にはUART,I2C,SPIがありますが、I2Cを利用しています。

## センサー
### 温湿度センサー(DHT20)
I2C接続で、温度と湿度を取得します。


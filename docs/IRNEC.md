
---

# NEC IR Receiver Module for Raspberry Pi Pico

**daichamame_ir_nec_decoder.py** は、Raspberry Pi Pico 上で  
**NEC方式の赤外線リモコン信号を受信するための MicroPython モジュール**です。

IRQ（割り込み）でパルス幅をリアルタイムに計測し、  
リーダー検出 → 0/1 判定 → 32bit 整合性チェックまで自動で行います。

アプリ側は **`read()` を呼ぶだけで最新の (addr, cmd) を取得**できます。

---

## 機能

- IRQ によるリアルタイムパルス計測  
- リーダー信号（9ms LOW + 4.5ms HIGH）を自動検出  
- 0/1 ビット判定（LOW パルス幅で判定）  
- 32bit 整合性チェック（NEC仕様）  
- 最新の値を内部に保持し、`read()` で取得可能  
- アプリ側はイベント駆動でシンプルに記述可能  

---

## 使用デバイス

### 送信機
- NECフォーマット準拠 赤外線リモコン（例：OE13KIR）

### 受信
- OSRB38C9AA（秋月電子）

---

## 接続

### IR Receiver
| Device | Pico |
|--------|------|
| OUT    | GP16 |
| VCC    | 3.3V |
| GND    | GND  |

---

## ファイル配置構成

```
  /
  ir_nec_ssd1306.py          ← サンプルアプリ
  lib/
    daichamame_ir_nec_decoder.py  ← NEC受信モジュール
    daichamame_ssd1306.py
    fontloader.py
  font/
    shnm8x16r.bdf            ← 東雲フォント（別途用意）
```

---

## 使用例

最小限の使用例：

```python
from daichamame_ir_nec_decoder import IRNECReceiver

ir = IRNECReceiver(pin=16)

while True:
    val = ir.read()
    if val:
        addr, cmd = val
        print(hex(addr), hex(cmd))
```

---

## サンプルアプリケーション (SSD1306 Display)

`ir_nec_ssd1306.py` では、  
受信したコマンドを SSD1306 OLED に表示するサンプルを提供しています。

- 100ms ごとに Timer 割り込みで `read()` を呼ぶ  
- ボタンが押されていれば画面更新  
- イベント駆動で拡張しやすい構成  

---

## Module Parameters

```python
IRNECReceiver(
    pin=16,
    leader_low=(8000, 10000),
    leader_high=(4000, 5000),
    bit0=(400, 900),
    bit1=(1200, 2000),
    noise_cut=300
)
```

| パラメータ | 説明 |
|-----------|------|
| leader_low | リーダー LOW パルス幅 |
| leader_high | リーダー HIGH パルス幅 |
| bit0 | 0 ビットの LOW パルス幅 |
| bit1 | 1 ビットの LOW パルス幅 |
| noise_cut | ノイズ除外閾値（us） |

受信モジュールの種類や周囲光によりパルス幅が変動するため、必要に応じて調整してください。

---


## License

MIT License

---


※ 東雲フォント（BDF）はライセンスの都合で同梱していません。


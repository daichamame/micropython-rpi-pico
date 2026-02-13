"""
モジュール名: daichamame_ir_nec_decoder.py
概要:
    NEC方式 赤外線リモコン受信モジュール。
    パルス幅の計測・リーダー検出・0/1判定・32bit整合性チェックを行い、値を返す。
    値によるキー判定は本モジュールでは行わない。
特徴:
    - IRQでリアルタイムにパルス幅を計測し、最新の値を保持
    - 値の取得は read() を呼ぶだけで最新の値を取得可能

使用デバイス:
    以下のデバイスを使用して作成しています
    送信：
      ＮＥＣフォーマット準拠 赤外線リモコン送信機 
    受信：
      赤外線リモコン受信モジュール OSRB38C9AA
      
注意点:
    - 周囲光や受信モジュールの種類によりパルス幅が変動するため、
    必要に応じてパラメータを調整すること

"""
from machine import Pin
import time

class IRNECReceiver:
    """
    初期化処理
        pin: 使用するGPIO番号（必須）
        leader_low:   (min_us, max_us) リーダーLOWパルス幅
        leader_high:  (min_us, max_us) リーダーHIGHパルス幅
        bit0:         (min_us, max_us) 0ビットのLOWパルス幅
        bit1:         (min_us, max_us) 1ビットのLOWパルス幅
        noise_cut:    ノイズ除外の閾値（us）
    """
    def __init__(self, pin,
                 leader_low=(8000, 10000),
                 leader_high=(4000, 5000),
                 bit0=(400, 900),
                 bit1=(1200, 2000),
                 noise_cut=300):

        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.leader_low = leader_low
        self.leader_high = leader_high
        self.bit0 = bit0
        self.bit1 = bit1
        self.noise_cut = noise_cut

        self.last = time.ticks_us()
        self.prev_diff = 0
        self.recording = False
        self.buf = []

        # pinのHigh/Low切り替え時に
        self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                     handler=self._detect_pulse)
        self.code32 = None  # 最新の32bitフレームを保持

    """
    パルスの検出
    GPIOの状態変化によって呼び出される
    """
    def _detect_pulse(self, pin):
        now = time.ticks_us()
        diff = time.ticks_diff(now, self.last)  # 前回との差分を取得
        self.last = now
        level = pin.value() #ピンのHigh/Lowを取得

        # ノイズ除外
        if diff < self.noise_cut:
            self.prev_diff = diff
            return

        # リーダー検出
        # 前回のパルス幅と、今回のパルス幅が範囲内かをチェックしリーダーを検出する
        if (self.leader_low[0] <= self.prev_diff <= self.leader_low[1] and
            self.leader_high[0] <= diff <= self.leader_high[1]):
            self.recording = True # リーダーコードを受信したステータス
            self.buf = []
            self.prev_diff = diff
            return

        # ビット判定には、LOW パルスのみを使用する
        if self.recording and level == 0:
            if self.bit0[0] <= diff <= self.bit0[1]:
                self.buf.append(0)
            elif self.bit1[0] <= diff <= self.bit1[1]:
                self.buf.append(1)

        # 32bit 揃ったら整合性チェック
        if self.recording and len(self.buf) == 32:
            self.recording = False
            self._set_code() # 16進数に変換

        self.prev_diff = diff

    """
    16進数に変換し、最新の状態として保持する
    """
    def _set_code(self):
        bits = self.buf
        # 1バイトずつ取得
        addr     = int("".join(str(b) for b in bits[0:8]), 2)
        addr_inv = int("".join(str(b) for b in bits[8:16]), 2)
        cmd      = int("".join(str(b) for b in bits[16:24]), 2)
        cmd_inv  = int("".join(str(b) for b in bits[24:32]), 2)

        # 整合性チェック（NEC の仕様）
        if (addr ^ addr_inv) != 0xFF or (cmd ^ cmd_inv) != 0xFF:
            return # 

        # 正常フレームとして保持
        self.code32 = (addr, cmd)

    """
    最新の (addr, cmd) を返す。その後、値をNoneに設定する
    """
    def read(self):
        f = self.code32
        self.code32 = None # 値を初期化する
        return f

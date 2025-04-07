"""
    RotalyEncoder
    ロータリーエンコーダから方向と値を取得する
    CW (Clockwise): 時計回り（右回り）
    CCW (Counter Clockwise): 反時計回り（左回り）

    処理概要:
    Pin Aの値がLOWとなるタイミング（割り込み）で変化をチェック
    Pin Aの値がHIGHとなったタイミングで、Pin Bの値で方向を判断
    CW/CCWを判定 以下の矢印のタイミング
    
    時計回り(CW)
    pin A   B
    HIGH  HIGH
    LOW   HIGH
    LOW   LOW
    HIGH  LOW <- 
    HIGH  HIGH

    反時計回り(CCW)
    pin A   B
    HIGH  HIGH
    HIGH  LOW
    LOW   LOW
    LOW   HIGH
    HIGH  HIGH <- 
"""
from machine import Pin

class ROTALY_ENCODER:
    HIGH = 1
    LOW  = 0
    def __init__(self, pin_a, pin_b,position,min_position=0,max_postion=255,step=1):
        """
            pin_a:AピンのGPIO
            pin_b:BピンのGPIO
            position:初期値
            min_position:最小値
            max_postion:最大値
            step:増減数（整数値）
        """
        self.pin_a = Pin(pin_a,Pin.IN,Pin.PULL_UP)
        self.pin_b = Pin(pin_b,Pin.IN,Pin.PULL_UP)
        self.pos = position
        self.minval = min_position
        self.maxval = max_postion
        self.stepval = step
        self.direction = None
        self.pin_a.irq(trigger=Pin.IRQ_FALLING,handler=self.determine_rotation_direction) # 割り込みを入れる
    # 回転方向を判断する
    def determine_rotation_direction(self,p):
        """
        direction:CW/CCW, pos:変化後の値をセットする
        """
        val_a = self.pin_a.value() # Pin Aの値取得
        # pin A がLOWの場合　　　　　　　
        if (val_a == self.LOW ):
            self.direction = None # 方向初期化
            # val_a がHIGHになるまで値を取得
            while (val_a == 0):
                val_a = self.pin_a.value()
                val_b = self.pin_b.value()
            # val_aがHIGHになった時に、val_bの値から方向を判断
            if val_b == self.LOW: # 時計回り
                if self.pos <= (self.maxval-self.stepval):  # 最大値より小さければプラス
                    self.pos += self.stepval
                else: # 既に最大値の場合、最小値を設定
                    self.pos = self.minval
                self.direction = "CW"
            else: # 反時計回り
                if self.pos >= (self.minval+self.stepval):   # 最小値より大きければマイナス
                    self.pos -= self.stepval
                else: # 既に最小値の場合、最大値を設定
                    self.pos = self.maxval
                self.direction = "CCW"
        return
    # 現在の状態を取得
    def read_position(self):
        """
        直前の方向と、現在の値を返す
        """
        return (self.direction,self.pos)
    # 現在の状態を設定
    def set_position(self,pos):
        """
        現在の状態を設定する
        """
        self.pos = pos

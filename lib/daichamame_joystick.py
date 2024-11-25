"""
    JoyStick
    縦方向と横方向、1つのボタンに対応
    縦方向、横方向の値は、ADCを利用
    ボタンは、IRQ_RISINGを使用した割り込み処理を利用
"""
from machine import Pin,ADC
import micropython
import time

class JOYSTICK(object):
    # GPIOの設定
    JYSTK_SW_PIN       = 22
    JYSTK_HORIZON_PIN  = 26
    JYSTK_VERTICAL_PIN = 27
    JYSTK_THRESHOLD = 1024
    
    swbtn = 0		# スイッチの状態
    v_center = 0	# 垂直方向の中心値
    h_center = 0	# 平衡方向の中心値
    vh_threshold = 0 # ジョイスティックの操作判定
    # 初期化
    def __init__(self,vertical=JYSTK_VERTICAL_PIN,horizon=JYSTK_HORIZON_PIN,switch=JYSTK_SW_PIN):
        self.adc_v = ADC(vertical) # 縦方向の値取得用
        self.adc_h = ADC(horizon)  # 横方向の値取得用
        self.sw = Pin(switch,Pin.IN,Pin.PULL_UP) # ボタン

    # 初期設定
    def init(self,threshold=JYSTK_THRESHOLD):
        # ジョイスティックを操作していない状態をセンター座標として取得
        self.v_center = 0
        self.h_center = 0
        self.vh_threshold = threshold
        (self.v_center,self.h_center) = self.read_data()
        #　ボタンが押された場合の割り込み処理
        self.sw.irq(trigger = Pin.IRQ_RISING,handler = self.callback_push_sw)

    # 縦横の値を取得（センターからの差分）
    def read_data(self):
        cnt=10
        v=[0] * cnt
        h=[0] * cnt
        v_avg=0
        h_avg=0
        # 水平、垂直方向の値を複数回取得
        for i in range(cnt):
            v[i] = self.adc_v.read_u16()
            h[i] = self.adc_h.read_u16()
        v.sort()
        h.sort()
        for i in range(1,cnt-1): # 最小値と最大値を除く値で平均
            v_avg += v[i]
            h_avg += h[i]
        v_avg=int(v_avg/(cnt-2))
        h_avg=int(h_avg/(cnt-2))
        # センター値との差を取得
        v_avg = v_avg - self.v_center
        h_avg = h_avg - self.h_center      
        return (v_avg,h_avg)
    # ボタンを押されたときに呼ばれる関数
    def callback_push_sw(self,sw):
        """ボタンが押保持"""
        if(self.swbtn==0):
            self.swbtn = 1    # ボタンが押されたら、ステータスを1
        return
    # 現在の状態を取得
    def get_sw_status(self):
        """ボタンが取得"""
        return self.swbtn
    # スイッチのステータスをリセット
    def sw_reset(self):
        """ リセット:0 """
        self.swbtn = 0
    # 方向キーのチェック
    def check_value(self):
        """ 無操作：0 左右、上下:1,-1 """
        (v,h)=self.read_data()
        rv = (abs(v) > self.vh_threshold)*((v>0)+(v<0)*(-1))
        rh = (abs(h) > self.vh_threshold)*((h>0)+(h<0)*(-1))
        return(rv,rh)

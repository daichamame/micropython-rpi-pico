"""
    この WireFrame モジュールは、ST7789 / ILI9341 / SSD1306 / 電子ペーパーなど、
    任意の表示デバイスで動作するデモ用ワイヤフレーム描画を想定しています。

    目的はリアルタイム描画ではなく、
    表示デバイスの描画速度・メモリ挙動・GC の動作を
    実測ベースで確認することにあります。

    Z 関数は mode により切り替え可能で、
    0: 減衰サイン、1: 渦巻き（Spiral）を選択できます。
"""
import math
import gc

class WireFrame(object):
    wf_struct={
        "step":10,
        "xy_span":40.0,
        "z_span":40.0,
        "count":11
    }
    zs = []
    
    # 初期化
    def __init__(self,step,xy_span,z_span,mode=0):
        """
            step:間隔
            xy_span:中心からのx軸、y軸の長さ
            z_span:z軸の高さ
            mode:0:減衰サイン、1:渦巻
            
        """
        self.wf_struct["step"] = step
        self.wf_struct["xy_span"] = xy_span
        self.wf_struct["z_span"] = z_span
        self.wf_struct["count"] = int((self.wf_struct["xy_span"] * 2)/step)+1
        self.zs = []
        # z を先に全部計算しておく（再利用用）
        for y in range(-xy_span,xy_span+1,step) :
            row = []
            for x in range(-xy_span,xy_span+1,step) :
                row.append(self._calc_z(x, y,mode))
            self.zs.append(row)

    # z軸の計算
    def _calc_z(self,x, y,mode):
        """
            x,yからmodeによってz軸を求める
        """
        r = math.sqrt(x*x + y*y)
        if mode == 1:
            # 渦巻き（Spiral）
            a = math.atan2(y, x)
            z=math.sin(r*0.15 + a*4) * self.wf_struct["z_span"] * 0.5
        else:
            # 減衰サイン（既定）
            z=math.sin(r*0.2) * math.exp(-r*0.03) * self.wf_struct["z_span"]
        return z
       
    # 回転データの作成
    # x,y,z座標と色を計算
    def project(self, ax, ay, az):
        """
            x軸、y軸、z軸に対して回転した座標を計算する
        """
        bitmap = []
        for j in range(self.wf_struct["count"]):
            y = -self.wf_struct["xy_span"] + j*self.wf_struct["step"]
            row = []
            for i in range(self.wf_struct["count"]):
                z = self.zs[j][i]
                x = -self.wf_struct["xy_span"] + i*self.wf_struct["step"]
                # 回転
                wx, wy, wz = self._rotate(x, y, z, ax, ay, az)
                # 投影
                sx = int(wx)
                sy = int(wy - wz * 0.3)
                # 色
                col = int(self._color_from_z(z))
                row.append((sx, sy, col))
            bitmap.append(row)
            gc.collect()
        return self.wf_struct["count"], self.wf_struct["count"], bitmap

    # 回転座標の取得
    def _rotate(self,x, y, z, ax, ay, az):
        """
            三角関数の加法定理で得られる 2D 回転式を、
            X → Y → Z の順に適用している
        """
        # 回転角をラジアンで取得
        cx = math.cos(ax)
        sx = math.sin(ax)
        cy = math.cos(ay)
        sy = math.sin(ay)
        cz = math.cos(az)
        sz = math.sin(az)

        # X軸回転したときのY,Zを求める
        # y2 = y*cos(ax)-z*sin(ax)
        # z2 = y*sin(ax)+z*cos(ax)
        y2 = y * cx - z * sx
        z2 = y * sx + z * cx
        # 次にY軸回転をしたときのX,Zを求める
        # x2 = x*cos(ay)-z2*sin(ay)
        # z3 = x*sin(ay)+z2*cos(ay)
        x2 = x * cy + z2 * sy
        z3 = -x * sy + z2 * cy
        # 最後にZ軸回転したときのX、Yを求める
        # x3 = x2*cos(az)-y2*sin(az)
        # y3 = x2*sin(az)+y2*cos(az)
        x3 = x2 * cz - y2 * sz
        y3 = x2 * sz + y2 * cz      
        return x3, y3, z3

    # 色の設定(zの値により変化)
    def _color_from_z(self,z):
        """
            zの値に対して色を設定する
        """
        t = (z + self.wf_struct["z_span"]) / (self.wf_struct["z_span"]*2)
        b = 255
        g = int(t * 255)
        r = int(t * 128)
        return (r<<16)|(g<<8)|b



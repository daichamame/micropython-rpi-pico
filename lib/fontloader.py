"""
このモジュールは、JIS X 0201コード規格に基づいたビットマップフォントを
読み込み、それらをリストに格納する簡易ツールです
"""

import re
import os
import gc

class FontLoader(object):
    # 初期処理
    def __init__(self,bdf_file_name):
        try:
            os.stat(bdf_file_name)
            self.filename = bdf_file_name
        except Exception as e:
            print(f"{e} {bdf_file_name}は存在しません。")

    # BDFファイルからリストに格納
    def load_font(self):
        fontdata=[]
        fontline=[]	# 1文字のフォント情報格納用
        b_flag=0	# ピクセル情報行判定
        file = open(self.filename, 'r')
        for line in file:
            line.strip()  # 改行を削除
            if line.startswith('ENCODING'):
                # ENCODING の後に続く数字を抽出
                charcode = re.search(r'ENCODING (([ 0-9]*))', line)
                str_addr=charcode.group(1).replace(" ", "") # スペースを取り除く
                addr=int(str_addr,10) # 数字に変換
                if addr >= 0xa1 and addr <= 0xbf:
                    fontline.append(0xEFBD00+addr) # アドレスを変換して格納
                elif addr >= 0xc0 and addr <= 0xdf:
                    fontline.append(0xEFBDC0+addr) # アドレスを変換して格納
                else:
                    fontline.append(addr)
            if line.startswith('ENDCHAR'): # ピクセル情報が終わりの場合
                fontdata.append(fontline) # 1文字の情報をフォントデータに格納
                fontline=[] # リストの初期化
                b_flag=0 # ピクセル行の判別初期化
                gc.collect() # 可変のfontlineを使用するため、メモリの解放
            if b_flag==1: # ピクセル情報ならば、fontlineに追加
                fontline.append(int(line.strip(), 16)) # 1文字のBITMAP情報リスト作成
            if line.startswith('BITMAP'):
                b_flag=1 # 次の行からピクセル情報
        file.close()
        sorted_fontdata = sorted(fontdata) # コード順に並べ替え
        return sorted_fontdata

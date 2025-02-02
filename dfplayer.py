import daichamame_dfplayer
import time

df = daichamame_dfplayer.DFPLAYER(uart_tx=16,uart_rx=17)
df.reset()			# リセット
df.set_volume(20)	#　音量設定
df.set_equalizer(1)	# イコライザー設定
print("現在の音量:" + str(df.get_volume()))
print("現在のイコライザー:" + str(df.get_equalizer()))
print("現在の曲:" + str(df.get_track()))
print("すべての曲数:" + str(df.get_total_count()))
# 繰り返し再生
print("繰り返し再生")
df.set_repeat_play()
time.sleep_ms(500)
print("現在のプレイモード:" + str(df.get_playmode()))
print("現在の曲 :" + str(df.get_track()))
time.sleep_ms(3000)

# フォルダ内繰り返し再生
print("フォルダ内繰り返し再生")
df.set_repeat_play_folder(1)
time.sleep_ms(1500)
print("現在のプレイモード:" + str(df.get_playmode()))
print("現在の曲 :" + str(df.get_track()))
time.sleep_ms(3000)

# 1曲の繰り返し再生
df.set_repeat_play_single(1)
time.sleep_ms(500)
print("1曲の繰り返し再生")
print("現在のプレイモード:" + str(df.get_playmode()))
print("現在の曲 :" + str(df.get_track()))
time.sleep_ms(3000)

# ランダム再生
df.set_random_play()
time.sleep_ms(500)
print("ランダム再生")
print("現在のプレイモード:" + str(df.get_playmode()))
print("現在の曲 :" + str(df.get_track()))



            


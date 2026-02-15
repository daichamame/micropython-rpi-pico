"""DHT20 sample"""
import daichamame_dht20

dht20=daichamame_dht20.DHT20()
ret=dht20.init()
print(ret)
(temp,hum)=dht20.get_data()
print(temp)
print(hum)

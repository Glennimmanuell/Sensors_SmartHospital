import paho.mqtt.client as mqtt
from collections import deque
from matplotlib import pyplot as plt

mqtt_server = '192.168.46.215'
topic_sub_temp = 'esp/dht/temperature_glenn'
topic_sub_hum = 'esp/dht/humidity_glenn'
topic_sub_air_quality = 'esp/mq135/air_quality_glenn'
topic_sub_heart_rate = 'esp/max30102/heartrate_glenn'

class dhtdata:
    def __init__(self, maxdata=1000):
        self.axis_x = deque(maxlen=maxdata)
        self.axis_temp = deque(maxlen=maxdata)
        self.axis_hum = deque(maxlen=maxdata)
        self.axis_air_quality = deque(maxlen=maxdata)
        self.axis_heart_rate = deque(maxlen=maxdata)

    def add(self, x, temp, hum, air_quality, heart_rate):
        self.axis_x.append(x)
        self.axis_temp.append(temp)
        self.axis_hum.append(hum)
        self.axis_air_quality.append(air_quality)
        self.axis_heart_rate.append(heart_rate)

def main():
    global data, plots
    data = dhtdata()
    print(data)
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Sensor Data: Temperature, Humidity, Air Quality, and Heart Rate")

    plots = {
        'temperature': dhtplot(axs[0, 0], "Temperature", 'r'),
        'humidity': dhtplot(axs[0, 1], "Humidity", 'b'),
        'air_quality': dhtplot(axs[1, 0], "Air Quality", 'g'),
        'heart_rate': dhtplot(axs[1, 1], "Heart Rate", 'm')
    }

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_server, 1883, 60) #timout 60 detik
    client.loop_start()

    count = 0
    while True:
        count += 1
        plt.pause(1)

class dhtplot:
    def __init__(self, axis, label, color):
        self.axis = axis
        self.lineplot, = axis.plot([], [], label=label, color=color)
        self.axis.set_title(label)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel(label)
        self.axis.legend()

    def plot(self, x, y):
        self.lineplot.set_data(x, y)
        self.axis.set_xlim(min(x), max(x))
        self.axis.set_ylim(min(y) - 5, max(y) + 5)
        

def on_connect(client, userdata, flags, rc):
    print("Puji Tuhan connect, result code = " + str(rc)) # 0 berhasil, 1 ditolak, 2 gagal, 3-255 ada kesalahan lain
    client.subscribe(topic_sub_temp)
    client.subscribe(topic_sub_hum)
    client.subscribe(topic_sub_air_quality)
    client.subscribe(topic_sub_heart_rate)
    for plot in plots.values():
        plot.axis.figure.canvas.draw()

def on_message(client, userdata, msg):
    global data, plots
    print(msg.topic + " " + msg.payload.decode())
    temp = None
    hum = None
    air_quality = None
    heart_rate = None
    if msg.topic == topic_sub_temp:
        temp = float(msg.payload.decode())
    elif msg.topic == topic_sub_hum:
        hum = float(msg.payload.decode())
    elif msg.topic == topic_sub_air_quality:
        air_quality = float(msg.payload.decode())
    elif msg.topic == topic_sub_heart_rate:
        heart_rate = float(msg.payload.decode())
    if temp is not None or hum is not None or air_quality is not None or heart_rate is not None:
        data.add(len(data.axis_x),
                 temp if temp is not None else data.axis_temp[-1] if data.axis_temp else 0,
                 hum if hum is not None else data.axis_hum[-1] if data.axis_hum else 0,
                 air_quality if air_quality is not None else data.axis_air_quality[-1] if data.axis_air_quality else 0,
                 heart_rate if heart_rate is not None else data.axis_heart_rate[-1] if data.axis_heart_rate else 0)
        plots['temperature'].plot(data.axis_x, data.axis_temp)
        plots['humidity'].plot(data.axis_x, data.axis_hum)
        plots['air_quality'].plot(data.axis_x, data.axis_air_quality)
        plots['heart_rate'].plot(data.axis_x, data.axis_heart_rate)
        

if __name__ == "__main__":
    main()

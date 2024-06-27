from machine import ADC, Pin
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import network

# Define MQTT topics for MQ135 sensor data
topic_pub_air_quality = b'esp/mq135/air_quality_glenn'

# Pin AO connected to GPIO32
adc = ADC(Pin(32))

# Define the minimum and maximum sensor values for MQ135
sensor_min = 0
sensor_max = 4095  # This value depends on the ADC resolution, adjust if needed

client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = '192.168.46.215'
ssid = 'IoT_Dev'
password = 'elektro234'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')

def connect_mqtt():
    global client_id, mqtt_server
    client = MQTTClient(client_id, mqtt_server)
    client.connect()
    print('Connected to %s MQTT broker' % (mqtt_server))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

def read_sensor():
    value = adc.read()
    return value

def map_value(value, min_val, max_val):
    # Map the value from the sensor's range to a percentage (0 to 100)
    return (value - min_val) / (max_val - min_val) * 100

try:
    client = connect_mqtt()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        air_quality = read_sensor()
        air_quality_percentage = map_value(air_quality, sensor_min, sensor_max)
        air_quality_integer = int(air_quality_percentage)  # Convert to integer
        print("Air quality:", air_quality_integer, "%")
        client.publish(topic_pub_air_quality, str(air_quality_integer))
        time.sleep(5)  # Adjust the interval as needed
    except OSError as e:
        restart_and_reconnect()




import RPi.GPIO as GPIO
import dht22
import time
import urllib.request
import urllib.error
import json
import sys
from http.client import HTTPConnection

config = json.load(sys.stdin)

hundredYears = 60*24*365*100

host = config['host']
port = config['port']
deviceId = config['deviceId']
sleepTime = config['everyMinutes'] * 60
numMeasurements = config.get('numMeasurements', hundredYears)

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 14
instance = dht22.DHT22(pin=4)

hostname = '{}:{}'.format(host, port)
connection = HTTPConnection(hostname)

time.sleep(1)
def sense():
    result = instance.read()
    while (not result.is_valid()):
        result = instance.read()
    temperature = "%.1f" % result.temperature
    humidity = "%.1f" % result.humidity
    values = '{}_{}'.format(temperature, humidity)
    requestPath = '/' + deviceId + '/' + values
    connection.request("PUT", requestPath)
    response = connection.getresponse()
    print(response)

count = 0
while True:
    try:
        sense()
        numMeasurements += 1
        if count >= numMeasurements:
            break
        time.sleep(sleepTime)
    except Exception as e:
        GPIO.cleanup()
        raise e

import RPi.GPIO as GPIO
import dht22
import time
import datetime

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 14
instance = dht22.DHT22(pin=4)

time.sleep(1)

result = instance.read()
while (not result.is_valid()):
    result = instance.read()
time = datetime.datetime.utcnow().isoformat(timespec = "milliseconds")
temperature = "%6.1f" % result.temperature
humidity = "%6.1f" % result.humidity
print("{} {} {}".format(time, temperature, humidity))

GPIO.cleanup()

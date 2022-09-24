# DHT22 Python library

Cloned from: https://github.com/bullet64/DHT22_Python

This simple class can be used for reading temperature and humidity values from DHT22 sensor on Raspberry Pi.

Original Source Code: https://github.com/szazo/DHT11_Python

# Usage

1. Instantiate the `DHT22` class with the pin number as constructor parameter.
2. Call `read()` method, which will return `DHT22Result` object with actual values and error code.

For example:

```python
import RPi.GPIO as GPIO
import dht22

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pin 14
instance = DHT22.DHT22(pin = 14)
result = instance.read()

if result.is_valid():
    print("Temperature: %-3.1f C" % result.temperature)
    print("Humidity: %-3.1f %%" % result.humidity)
else:
    print("Error: %d" % result.error_code)
```

For working example, see `dht22_example.py` (you probably need to adjust pin for your configuration)


# License

This project is licensed under the terms of the MIT license.

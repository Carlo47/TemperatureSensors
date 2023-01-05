# Temperature and Humidity Sensors
This Python program shows how to query the sensors DHT11, DHT22, DS18B20 and SHT31
connected to a ESP8266 board loaded with the firmware [micropython](https://micropython.org).

Each module for the different sensors implements the method `getValues()`, 
which returns a list of available measurement values **[tC, tF, rH, dP]**, namely the
temperature in °Celsius and °Fahrenheit, the relative humidity in % and the
computed dew point in °Celsius.

The DS18B20 temperature sensor only provides the temperature values [tC, tF]. 

For a quick function check the method `printValues()` is implemented.

The `main.py` implements also the method `waitIsOver()`, which is used to periodically query the sensors without blocking the main loop. As an argument, it takes a list which holds the previous ticks and the query period.

The sample program generates the output below:

```
Number of detected DS18B20-Sensors = 1

DHT11
-----
tC = 22.0 °C
tF = 71.6 °F
rH = 49.0 %
dp = 10.8 °💧

DHT22
-----
tC = 22.2 °C
tF = 72.0 °F
rH = 48.9 %
dp = 10.9 °💧

DS18B20
-------
tC = 22.3 °C
tF = 72.2 °F

SHT31
-----
tC = 22.6 °C
tF = 72.6 °F
rH = 48.6 %
dp = 11.2 °💧
```
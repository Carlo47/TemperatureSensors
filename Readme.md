# Temperature and Humidity Sensors
This Python program shows how to query the sensors DHT11, DHT22, DS18B20, SHT31 and BME280
connected to a ESP8266 board loaded with the firmware [micropython](https://micropython.org).

Each module for the different sensors implements the method `getValues()`, 
which returns a list of available measurement values **[tC, tF, rH, dP]**, namely the
temperature in °Celsius and °Fahrenheit, the relative humidity in % and the
computed dew point in °Celsius.

For a quick function check the method `printValues()` is implemented.

The **DS18B20** sensor only provides the temperature values **[tC, tF]**.

The **BME280** sensor also measures local air pressure. The local normal pressure is 
calculated from the specified local altitude in meters above sea level. These 
two values show the tendency of the air pressure, which allows a weather forecast.
The method getValues() returns the list **[tC, tF, rH, dP, airPres, locNormalPres, locAltitude]**

The `main.py` implements also the method `waitIsOver()`, which is used to periodically query the sensors without blocking the main loop. As an argument, it takes a list which holds the previous ticks and the query period.

The sample program generates the output below:

```
Number of detected DS18B20-Sensors = 1

Device addresses found on I2C-bus:    
[0x44, 0x76]

DHT11
-----
tC = 23.0 °C
tF = 73.4 °F
rH = 41.0 %  
dP =  9.0 °💧

DHT22        
-----        
tC = 23.3 °C
tF = 73.9 °F
rH = 43.2 %  
dP = 10.1 °💧

DS18B20      
-------      
tC = 22.6 °C
tF = 72.7 °F

SHT31
-----
tC = 23.1 °C
tF = 73.5 °F
rH = 44.1 %  
dP = 10.2 °💧

BME280       
-----        
tC = 21.4 °C 
tF = 70.6 °F 
rH = 40.6 %  
dP =  7.5 °💧
airPres = 960.7 hPa
localNP = 965.5 hPa
locAlt  = 405 masl
```
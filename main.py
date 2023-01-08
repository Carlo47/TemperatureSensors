"""
Module      main.py
Author      2023-01-01 Charles Geiser (https://www.dodeka.ch)

Purpose     Shows the use of the temperature and humidity 
            sensors DHT11, DHT22, DS18B20 and SH31

Board       ESP8266
Firmware    micropython from https://micropython.org

Wiring      DHT11-Sensor                        DHT22-Sensor
            .-----------.                       .-------.
            |  GND  (1) o--> GND                |  GND  o--> GND
            |  Vcc  (2) o--> 3.3V               |  NC   o NC
            |  DATA (3) o--> GPIO12             |  DATA o--> GPIO13
            '-----------'                       |  Vcc  o--> 3.3V
                                                '-------'  

            DS18B20-Sensor              SHT31-Sensor          BME280-Sensor
            .-----------.               .------.               .------.
            |  DATA (1) o--> GPIO0      |  SAA o--> GPIO4      |  Vcc o--> 3.3V 
            |  Vcc  (2) o--> 3.3V       |  SCL o--> GPIO5      |  GND o--> GND
            |  GND  (3) o--> GND        |  GND o--> GND        |  SCL o--> GPIO5
            '-----------'               |  Vcc o--> 3.3V       |  SDA o--> GPIO4
                                        '------'               |  CSB o NC 
                                                               |  SDO o NC
                                                               '------'

                                USB 
                    .-----------I...I-----------.
                    | ( )   [o] |   | [o]   ( ) |   
                    |     Flash '---' Reset     |
                    o 3V3                   Vin o
                    o GND                   GND o
             GPIO1  o TX                    RST o
             GPIO3  o RX                     EN o
             GPIO15 o D8                    3V3 o
             GPIO13 o D7                    GND o
             GPIO12 o D6                    CLK o SCLK
             GPIO14 o D5                    SD0 o MISO
                    o GND    ...........    CMD o CS
                    o 3V3   I           I   SD1 o MOSI
             GPIO2  o D4    I  ESP8266  I   SD2 o GPIO9
             GPIO0  o D3    I           I   SD3 o GPIO10
             GPIO4  o D2    I           I   RSV o
             GPIO5  o D1    I           I   RSV o
             GPIO16 o D0    I...........I   AD0 o ADC0
                    |       |  _   _  | |       |
                    | ( )   |_| |_| |_|_|   ( ) |
                    '---------------------------'
"""

from machine       import Pin, I2C
from dht11Sensor   import DHT11Sensor
from dht22Sensor   import DHT22Sensor
from ds18b20Sensor import DS18B20Sensor
from bme280Sensor  import BME280Sensor
import sht31Sensor
import time

ledBuiltin = const(2)
led = Pin(ledBuiltin, Pin.OUT)

sensorDHT11 = DHT11Sensor(Pin(12))
sensorDHT22 = DHT22Sensor(Pin(13))
sensorDS18B20 = DS18B20Sensor(Pin(0))

print('\n\nNumber of detected DS18B20-Sensors = %d' % sensorDS18B20.getNbrSensors())

i2c = I2C(sda=Pin(4), scl=Pin(5))
addrs = i2c.scan()
print('\nDevice addresses found on I2C-bus: ')
print('[{}]'.format(', '.join(hex(x) for x in addrs)))

sensorSHT31 = sht31Sensor.SHT31Sensor(i2c) # default i2c address used 0x44
sensorBME280 = BME280Sensor(i2c=i2c)       # default i2c address used 0x76
sensorBME280.localAltitude = 405           # my local altitude above sea level

msSensorCycle = [0, 15000]  # holds previous ticks and period of cycle in milliseconds

ledPeriod = 1000    # blink builtin led every second
ledPulsewidth = 50  # for 50ms

""" 
    Returns true when the specified time has elapsed
    msCycle = [msPrevious, msCycle] is a globally defined list
    which holds the previus ticks_ms and the ms to wait
"""
def waitIsOver(msCycle):
    if (time.ticks_ms() - msCycle[0] >= msCycle[1]):
        msCycle[0] = time.ticks_ms()
        return True
    else:
        return False

while True:
    led.value(0 if (time.ticks_ms() % ledPeriod < ledPulsewidth) else 1)

    if waitIsOver(msSensorCycle):
        print('\nDHT11\n-----')
        sensorDHT11.printValues()

        print('DHT22\n-----')
        sensorDHT22.printValues()

        print('DS18B20\n-------')
        sensorDS18B20.printValues(0)

        print('SHT31\n-----')
        sensorSHT31.printValues()

        print('BME280\n-----')
        sensorBME280.printValues()

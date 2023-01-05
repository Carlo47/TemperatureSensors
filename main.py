"""
Module      main.py
Author      2023-01-01 Charles Geiser (https://www.dodeka.ch)

Purpose     Shows the use of the temperature and humidity 
            sensors DHT11, DHT22, DS18B20 and SH31

Board       ESP8266
Firmware    micropython from https://micropython.org

Wiring      DHT11-Sensor Breakout Elegoo            DHT22-Sensor
            ----.                                   ----.
                o--- (1) GND  --> GND                   o--- (4) GND  --> GND
                o--- (2) Vcc  --> 3.3V                  o--- (3) NC
                o--- (3) DATA --> GPIO12                o--- (2) DATA --> GPIO13
            ----'                                       o--- (1) Vcc  --> 3.3V

            DS18B20-Sensor                          SHT31-Sensor
            ----.                                   ----.
                o--- (1) DATA --> GPIO0                 o--- SAA --> GPIO4
                o--- (2) Vcc  --> 3.3V                  o--- SCL --> GPIO5
                o--- (3) GND  --> GND                   o--- GND --> GND
            ----'                                       o--- Vcc --> 3.3V
                                                    ----'


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
import sht31Sensor
import time

ledBuiltin = const(2)
led = Pin(ledBuiltin, Pin.OUT)

sensorDHT11 = DHT11Sensor(Pin(12))
sensorDHT22 = DHT22Sensor(Pin(13))
sensorDS18B20 = DS18B20Sensor(Pin(0))
i2c = I2C(sda=Pin(4), scl=Pin(5))
addr = i2c.scan()[0]
sensorSHT31 = sht31Sensor.SHT31Sensor(i2c, addr)

def waitIsOver(msCycle):
    if (time.ticks_ms() - msCycle[0] >= msCycle[1]):
        msCycle[0] = time.ticks_ms()
        return True
    else:
        return False

msSensorCycle   = [0, 10000]  # holds previous ticks and period of cycle in milliseconds

ledPeriod = 1000
ledPulsewidth = 50

print('\n\nNumber of detected DS18B20-Sensors = %d' % sensorDS18B20.getNbrSensors())

while True:
    led.value(0 if (time.ticks_ms() % ledPeriod < ledPulsewidth) else 1)

    if waitIsOver(msSensorCycle):
        print('DHT11\n-----')
        sensorDHT11.printValues()

        print('DHT22\n-----')
        sensorDHT22.printValues()

        print('DS18B20\n-------')
        sensorDS18B20.printValues(0)

        print('SHT31\n-----')
        sensorSHT31.printValues()

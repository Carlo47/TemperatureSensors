"""
Module      ds18b20Sensor.py
Author      2023-01-01 Charles Geiser (https://www.dodeka.ch)

Purpose     Reads a DS18B20 temperature sensor connected
            to the supplied pin and provides the methods
                - getCelsius(sensorNbr)      temperature in °C
                - getFahrenheit(sensorNbr)   temperature in °F
                - printValues(sensorNbr)     prints the measured values to the terminal as
                                                tC = 20.9 °C
                                                tF = 69.6 °F

Board       ESP8266
Firmware    micropython from https://micropython.org

Usage       # Code in main program:
            from ds18b20Sensor import DS18B20Sensor
            sensorDS18B20 = DS18B20Sensor(Pin(16))
            sensorDS18B20.printValues(sensorNbr)
"""
import time, onewire
from ds18x20 import DS18X20

class DS18B20Sensor:

    def __init__(self, pin):
        self.ow = onewire.OneWire(pin)
        self.sensors = DS18X20(self.ow)
        self.addrs = self.sensors.scan()
        self.tC = self.tF = 0

    def getCelsius(self, sensorNbr):
        self.sensors.convert_temp()
        time.sleep_ms(750) # mandatory according datasheet
        self.tC = self.sensors.read_temp(self.addrs[sensorNbr])
        return self.tC

    def getFahrenheit(self, sensorNbr):
        self.tC = self.getCelsius(sensorNbr)
        self.tF = self.tC * 1.8 + 32.0
        return self.tF

    def printValues(self, sensorNbr):
        self.tF = self.getFahrenheit(sensorNbr)
        print('tC = %4.1f °C\ntF = %4.1f °F\n' % (self.tC, self.tF))

    def getNbrSensors(self):
        return len(self.addrs)

"""
Module      dht22Sensor.py
Author      2023-01-01 Charles Geiser (https://www.dodeka.ch)

Purpose     Reads a DHt22 temperature and humidity sensor connected
            to the supplied pin and provides the methods
                - getCelsius()      temperature in °C
                - getFahrenheit()   temperature in °F
                - getHumidity()     relative humidity in %
                - getDewpoint()     dew point in °C
                - printValues()     prints the measured values to the terminal as
                                        tC = 23 °C
                                        tF = 73 °F
                                        rH = 49 %
                                        dP = 12 °💧

Board       ESP8266
Firmware    micropython from https://micropython.org

Usage       # Code in main program:
            from dht11Sensor import DHT11Sensor
            sensorDHT22 = DHT22Sensor(Pin(13))
            sensorDHT22.printValues()
            v = sensorDHT22.getValues()
            print('relative humidity is %4.1f %%\n' % v[2])
"""
from dht import DHT22
from math import log

class DHT22Sensor:
    def __init__(self, pin):
        self.sensor = DHT22(pin)
        self._values = [0,0,0,0]

    def getValues(self):
        self.sensor.measure()
        self._values[0] = self.sensor.temperature()
        self._values[1] = self._values[0] * 1.8 + 32.0
        self._values[2] = self.sensor.humidity()
        k = log(self._values[2] / 100) + (17.62 * self._values[0]) / (243.12 + self._values[0])
        self._values[3] = 243.12 * k / (17.62 - k)
        return self._values

    def printValues(self):
        self.getValues()
        print('tC = %4.1f °C\ntF = %4.1f °F\nrH = %4.1f %%\ndP = %4.1f °💧\n' % (self._values[0], self._values[1], self._values[2], self._values[3]))
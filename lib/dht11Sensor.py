"""
Module      dht11Sensor.py
Author      2022-12-31 Charles Geiser (https://www.dodeka.ch)

Purpose     Reads a DHt11 temperature and humidity sensor connected
            to the supplied pin and provides the methods
                - getValues()       returns a list of measurements [tC, tF, rH, dP]
                - printValues()     prints the measured values to the terminal as
                                        tC = 23 °C
                                        tF = 73 °F
                                        rH = 49 %
                                        dP = 12 °💧

Board       ESP8266
Firmware    micropython from https://micropython.org

Usage       # Code in main program:
            from dht11Sensor import DHT11Sensor
            sensorDHT11 = DHT11Sensor(Pin(12))
            sensorDHT11.printValues()
            v = sensorDHT11.getValues()
            print('Temperature Fahrenheit is %d\n' % v[1])
"""
from dht import DHT11
from math import log

class DHT11Sensor:
    def __init__(self, pin):
        self.sensor = DHT11(pin)
        self._values = [0,0,0,0]

    def getValues(self):
        self.sensor.measure()
        self._values[0] = self.sensor.temperature()    # tC
        self._values[1] = self._values[0] * 1.8 + 32.0 # tF
        self._values[2] = self.sensor.humidity()
        k = log(self._values[2] / 100) + (17.62 * self._values[0]) / (243.12 + self._values[0])
        self._values[3] = 243.12 * k / (17.62 - k)
        return self._values

    def printValues(self):
        self.getValues()
        #print('tC = %02d °C\ntF = %02d °F\nrH = %02d %%\ndp = %2.0f °💧\n' % (self.tC, self.tF, self.rH, self.dP))
        print('tC = %4.1f °C\ntF = %4.1f °F\nrH = %4.1f %%\ndP = %4.1f °💧\n' % (self._values[0], self._values[1], self._values[2], self._values[3]))
    
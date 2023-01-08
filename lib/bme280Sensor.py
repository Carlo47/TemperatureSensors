# Authors: Paul Cunnane 2016, Peter Dahlebrg 2016
#
# This module borrows from the Adafruit BME280 Python library. Original
# Copyright notices are reproduced below.
#
# Those libraries were written for the Raspberry Pi. This modification is
# intended for the MicroPython and esp8266 boards.
#
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Based on the BMP280 driver with BME280 changes provided by
# David J Taylor, Edinburgh (www.satsignal.eu)
#
# Based on Adafruit_I2C.py created by Kevin Townsend.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time
from ustruct import unpack, unpack_from
from array import array
from math import log, pow

# BME280 default address.
BME280_I2CADDR = 0x76

# Operating Modes
BME280_OSAMPLE_1 = 1
BME280_OSAMPLE_2 = 2
BME280_OSAMPLE_4 = 3
BME280_OSAMPLE_8 = 4
BME280_OSAMPLE_16 = 5

BME280_REGISTER_CONTROL_HUM = 0xF2
BME280_REGISTER_CONTROL = 0xF4

class BME280Sensor:
    def __init__(self,
                 mode=BME280_OSAMPLE_1,
                 address=BME280_I2CADDR,
                 i2c=None,
                 **kwargs):
        # Check that mode is valid.
        if mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                        BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected mode value {0}. Set mode to one of '
                'BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or '
                'BME280_ULTRAHIGHRES'.format(mode))
        self._mode = mode
        self._address = address
        self._values = [0,0,0,0,0,0,0] # [tC, tF, rH, dP, airPres, locNP, locAlt]
        if i2c is None:
            raise ValueError('An I2C object is required.')
        self.i2c = i2c

        # load calibration data
        buf = self.i2c.readfrom_mem(self._address, 0x88, 26) # dig_T1..dig_H1
        #print(buf)
        #print(", ".join(hex(b) for b in buf)) 
        self.dig_T1, self.dig_T2, self.dig_T3, self.dig_P1, \
            self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, \
            self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9, \
            _, self.dig_H1 = unpack("<HhhHhhhhhhhhBB", buf)
        #print(unpack("<HhhHhhhhhhhhBB", buf))

        buf = self.i2c.readfrom_mem(self._address, 0xE1, 7) #dig_H2..dig_H6
        self.dig_H2, self.dig_H3 = unpack("<hB", buf)

        e4_sign = unpack_from("<b", buf, 3)[0]
        self.dig_H4 = (e4_sign << 4) | (buf[4] & 0xF)

        e6_sign = unpack_from("<b", buf, 5)[0]
        self.dig_H5 = (e6_sign << 4) | (buf[4] >> 4)

        self.dig_H6 = unpack_from("<b", buf, 6)[0]

        self.i2c.writeto_mem(self._address, BME280_REGISTER_CONTROL,
                             bytearray([0x3F]))
        self.t_fine = 0

        # temporary data holders which stay allocated
        self._l1_barray = bytearray(1)
        self._l8_barray = bytearray(8)
        self._l3_resultarray = array("i", [0, 0, 0])

    def read_raw_data(self, result):
        """ Reads the raw (uncompensated) data from the sensor.
            Args:
                result: array of length 3 or alike where the result will be
                stored, in temperature, pressure, humidity order
            Returns:
                None
        """
        self._l1_barray[0] = self._mode
        self.i2c.writeto_mem(self._address, BME280_REGISTER_CONTROL_HUM,
                             self._l1_barray)
        self._l1_barray[0] = self._mode << 5 | self._mode << 2 | 1
        self.i2c.writeto_mem(self._address, BME280_REGISTER_CONTROL,
                             self._l1_barray)

        sleep_time = 1250 + 2300 * (1 << self._mode)
        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        time.sleep_us(sleep_time)  # Wait the required time

        # burst readout from 0xF7 to 0xFE, recommended by datasheet
        self.i2c.readfrom_mem_into(self._address, 0xF7, self._l8_barray)
        readout = self._l8_barray
        # pressure(0xF7): ((msb << 16) | (lsb << 8) | xlsb) >> 4
        raw_press = ((readout[0] << 16) | (readout[1] << 8) | readout[2]) >> 4
        # temperature(0xFA): ((msb << 16) | (lsb << 8) | xlsb) >> 4
        raw_temp = ((readout[3] << 16) | (readout[4] << 8) | readout[5]) >> 4
        # humidity(0xFD): (msb << 8) | lsb
        raw_hum = (readout[6] << 8) | readout[7]

        result[0] = raw_temp
        result[1] = raw_press
        result[2] = raw_hum

    def read_compensated_data(self, result=None):
        """ Reads the data from the sensor and returns the compensated data.

            Args:
                result: array of length 3 or alike where the result will be
                stored, in temperature, pressure, humidity order. You may use
                this to read out the sensor without allocating heap memory

            Returns:
                array with temperature, pressure, humidity. Will be the one from
                the result parameter if not None
        """
        self.read_raw_data(self._l3_resultarray)
        raw_temp, raw_press, raw_hum = self._l3_resultarray
        # temperature
        var1 = ((raw_temp >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
        var2 = (((((raw_temp >> 4) - self.dig_T1) *
                  ((raw_temp >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) >> 8

        # pressure
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = (((var1 * var1 * self.dig_P3) >> 8) +
                ((var1 * self.dig_P2) << 12))
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            pressure = 0
        else:
            p = 1048576 - raw_press
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.dig_P8 * p) >> 19
            pressure = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)

        # humidity
        h = self.t_fine - 76800
        h = (((((raw_hum << 14) - (self.dig_H4 << 20) -
                (self.dig_H5 * h)) + 16384)
              >> 15) * (((((((h * self.dig_H6) >> 10) *
                            (((h * self.dig_H3) >> 11) + 32768)) >> 10) +
                          2097152) * self.dig_H2 + 8192) >> 14))
        h = h - (((((h >> 15) * (h >> 15)) >> 7) * self.dig_H1) >> 4)
        h = 0 if h < 0 else h
        h = 419430400 if h > 419430400 else h
        humidity = h >> 12

        if result:
            result[0] = temp
            result[1] = pressure
            result[2] = humidity
            return result
        else:
            return array("i", (temp, pressure, humidity))

    """
        Calculate local normal air pressure at given altitude
        kapa = 1.235
        K0 = kapa / (kapa -1) = 5.255
        T0 = 288.15 °K = 15 °C (According an international convention this temperatur is used as reference)
        gradT = 0.0065 K/m (Temperature gradient Kelvin / Meter
        P0 = 1013.25 hPa (accord. int. convention, P0 = pSeaLevel))
        H0 = T0 / gradT = 44330 m
        pLocal = P0 * (1 - h/H0) ^ K0
    """
    def calculateNpLocal(self, locAlt):
        self.values[5] = 1013.25 * pow( (1.0 - locAlt / 44330.0), 5.255)
        return self.values[5]

    """ Get list of measured/computed values [tCelsius, tFahrenheit, relHumidity, dewPoint, airPressure, localNP, localAlt]"""
    def getValues(self):
        self._values[0], self._values[4], self._values[2] = self.read_compensated_data() # tC, airPres, rH
        self._values[0] /= 100 # tC (temperature °Celsius)
        self._values[1] = self._values[0] * 1.8 + 32.0 # tF (temperature °Fahrenheit)
        self._values[2] /= 1024 # rH (relative humidity)
        self._values[4] /= 25600 # airPres (air pressure)
        k = log(self._values[2] / 100) + (17.62 * self._values[0]) / (243.12 + self._values[0])
        self._values[3] = 243.12 * k / (17.62 - k) # dP (dew point)
        self._values[5] = 1013.25 * pow( (1.0 - self._values[6] / 44330.0), 5.255) # loaclNP (local normal pressure)
        return self._values

    """ Print list of measured/computed values """
    def printValues(self):
        self.getValues()
        print('tC = %4.1f °C\ntF = %4.1f °F\nrH = %4.1f %%\ndP = %4.1f °💧\nairPres = %5.1f hPa\nlocalNP = %5.1f hPa\nlocAlt  = %d masl\n' % \
                (self._values[0], self._values[1], self._values[2], self._values[3], self._values[4], self._values[5], self._values[6]))

    """ Get local altitude """
    @property
    def localAltitude(self):
        return self._values[6]

    """ Set local altitude in meter above sea level """
    @localAltitude.setter
    def localAltitude(self, locAlt):
        self._values[6] = locAlt

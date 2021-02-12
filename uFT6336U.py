# Copyright (c) 2021 Alan Peaty
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# https://github.com/fantasticdonkey/uFT6336U

"""
MicroPython I2C driver for the Focus LCDs FT6336U capacitive touch panel controller IC.
Combine with the configuration of an interrupt pin on the host for best user experience.
"""

__version__ = "0.1.0"

# pylint: disable=import-error
from micropython import const

# Default I2C address of the FT6336U. Driver not tested with any other models.
I2C_ADDRESS = const(0x38)

# FT6336U I2C registers. Most are not used by this driver but are included for future use.
# If required, they can be directly addressed using the driver's low level functions.
# Refer to the FT6336U datasheet for details on how to interact with these registers.
REG_MODE_SWITCH = const(0x00)
REG_TD_STATUS = const(0x02)
REG_P1_XH = const(0x03)
REG_P1_XL = const(0x04)
REG_P1_YH = const(0x05)
REG_P1_YL = const(0x06)
REG_P1_WEIGHT = const(0x07)
REG_P1_MISC = const(0x08)
REG_P2_XH = const(0x09)
REG_P2_XL = const(0x0A)
REG_P2_YH = const(0x0B)
REG_P2_YL = const(0x0C)
REG_P2_WEIGHT = const(0x0D)
REG_P2_MISC = const(0x0E)
REG_ID_G_THGROUP = const(0x80)
REG_ID_G_THDIFF = const(0x85)
REG_ID_G_CTRL = const(0x86)
REG_ID_G_TIMEENTERMONITOR = const(0x87)
REG_ID_G_PERIODACTIVE = const(0x88)
REG_ID_G_PERIODMONITOR = const(0x89)
REG_ID_G_FREQ_HOPPING_EN = const(0x8B)
REG_ID_G_TEST_MODE_FILTER = const(0x96)
REG_ID_G_CIPHER_MID = const(0x9F)
REG_ID_G_CIPHER_LOW = const(0xA0)
REG_ID_G_LIB_VERSION_H = const(0xA1)
REG_ID_G_LIB_VERSION_L = const(0xA2)
REG_ID_G_CIPHER_HIGH = const(0xA3)
REG_ID_G_MODE = const(0xA4)
REG_ID_G_PMODE = const(0xA5)
REG_ID_G_FIRMID = const(0xA6)
REG_ID_G_FOCALTECH_ID = const(0xA8)
REG_ID_G_VIRTUAL_KEY_THRES = const(0xA9)
REG_ID_G_IS_CALLING = const(0xAD)
REG_ID_G_FACTORY_MODE = const(0xAE)
REG_ID_G_RELEASE_CODE_ID = const(0xAF)
REG_ID_G_FACE_DEC_MODE = const(0xB0)
REG_ID_G_STATE = const(0xBC)

DEVICE_MODE_WORKING = const(0x00)
DEVICE_MODE_FACTORY = const(0x40)

# CHIP_CODE_FT6236G = const(0x00)
# CHIP_CODE_FT6336G = const(0x01)
CHIP_CODE_FT6336U = const(0x02)
# CHIP_CODE_FT6426 = const(0x03)

class FT6336U():
    """ Focus LCDs' FT6336U driver and its interfaces """
    read_buffer = bytearray(2)

    def __init__(self, i2c, rst=None):
        """ Requires valid MicroPython I2C object """
        if I2C_ADDRESS not in i2c.scan():
            raise OSError("Chip not detected")
        self.i2c = i2c
        self.rst = rst
        if self._readfrom_mem(REG_ID_G_CIPHER_LOW) != CHIP_CODE_FT6336U:
            raise OSError("Unsupported chip")
        # Set chip to working mode, although not clear if this happens by default
        self.set_mode_working()

    def _readfrom_mem(self, register, num_bytes=1):
        """ Low level method to read from I2C register. Currenly supports up to 2 bytes. """
        self.i2c.readfrom_mem_into(I2C_ADDRESS, register, self.read_buffer)
        if num_bytes == 1:
            return int.from_bytes(self.read_buffer, "large") >> 8
        if num_bytes == 2:
            return int.from_bytes(self.read_buffer, "large")
        raise ValueError("Unsupported buffer size")

    def _writeto_mem(self, register, data):
        """ Low level method to write I2C register. """
        self.i2c.writeto_mem(I2C_ADDRESS, register, bytes(data))

    def set_mode_working(self):
        """ Set chip to working mode. """
        self._writeto_mem(REG_MODE_SWITCH, DEVICE_MODE_WORKING)

    def set_mode_factory(self):
        """ Set chip to factory mode. """
        self._writeto_mem(REG_MODE_SWITCH, DEVICE_MODE_FACTORY)

    def get_points(self):
        """ Get number of points detected. Supports up to 2 points. """
        return self._readfrom_mem(REG_TD_STATUS)

    def get_p1_x(self):
        """ Get X coordinates of point 1. """
        # Consecutive registers (REG_P1_XH and REG_P1_XL) are read.
        return self._readfrom_mem(REG_P1_XH, num_bytes=2) & 0x0FFF

    def get_p1_y(self):
        """ Get Y coordinates of point 1. """
        # Consecutive registers (REG_P1_YH and REG_P1_YL) are read.
        return self._readfrom_mem(REG_P1_YH, num_bytes=2) & 0x0FFF

    def get_p2_x(self):
        """ Get X coordinates of point 2. """
        # Consecutive registers (REG_P2_XH and REG_P2_XL) are read.
        return self._readfrom_mem(REG_P2_XH, num_bytes=2) & 0x0FFF

    def get_p2_y(self):
        """ Get Y coordinates of point 2. """
        # Consecutive registers (REG_P2_YH and REG_P2_YL) are read.
        return self._readfrom_mem(REG_P2_YH, num_bytes=2) & 0x0FFF

    def get_positions(self):
        """
        Consolidated method to get all x and y coordinates.
        Returns a list of tuples for points 1 and 2.
        """
        positions = []
        num_points = self.get_points()
        if num_points > 0:
            positions.append((self.get_p1_x(),self.get_p1_y()))
        if num_points > 1:
            positions.append((self.get_p2_x(),self.get_p2_y()))
        return positions

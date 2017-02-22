from I2C_bus import I2C_bus #Mazoum
from ctypes import c_int
from robot import Robot
from big_robot import *

print(I2C_bus.init(115200))
print(I2C_bus.init(9600))
print(I2C_bus.ping(130))
print(I2C_bus.init(115200))
print(I2C_bus.ping(130))

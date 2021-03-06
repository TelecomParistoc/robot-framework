# Robot Framework

## Installation
You must install the python framework if you want to use it in your projects. 
```
$ sudo make install
```

## Overview 

This framework is designed to provide a nice environment for programming Telecom Robotics robots.
It's split in several layers:
  - **Autorun** : a basic program whose role is to start the "main" program if a condition is meant
  - **Framework**: written in Python, it provides high-level abstraction to be used by user code
  - **py binding** : a binding in Python to provide clean interface (and maybe some high level functions)
to call low-level C functions.
  - **lib layer**: C libraries to deal with low-level stuff on the Raspberry-Pi
  - **controllers & other**: C code to manage specific components.

The following figure shows the organization of these layers:
![Framework schema](./doc/framework_schema.png)

### Autorun
This module is responsible of starting the robot software when powering up the Raspberry-Pi.
Complete documentation (in french) can be found [here](./startup_autolaunch/README.md).

### MotorController
This code runs on MotorBoard, which is the PCB board designed at Telecom Robotics to handle all
the low-level stuff related to movements.
Code can be found [here](https://github.com/TelecomParistoc/MotorController) and board design [here](https://github.com/TelecomParistoc/motorboard).
It can control
  - Motors
  - Coding wheels
  - IMU
  - RadioController data

### RadioController
This code runs on RadioBoard, which is the PCB board designed at Telecom Robotics.
This board is meant to provide localisation to the robots. During the matches, there is
one RadioBoard on each of the three beacons plots and one on each of the robots (both friends and foes).
The repository for this code can be found [here](https://github.com/TelecomParistoc/Beacons) and the
board design [here](https://github.com/TelecomParistoc/radioboard).

### libAX12
This library provides various functions to make use of AX12 digital servomotors. It's
meant to run on the Raspberry-Pi. It exposes Python and Javascript bindings for an
easy use. More info can be found [here](https://github.com/TelecomParistoc/libAX12).

### GPIO
Code in folder rpi_gpio contains capabilities of managing GPIO in python easily (and associate specific callbacks when value changes).
Note that it is more or less a T�l�com Robotics version of the python library RPi.GPIO.
It exposes an example gpio_test.py before any documentation would be available. More info can be found [here](https://github.com/TelecomParistoc/robot-framework/tree/master/rpi_gpio)

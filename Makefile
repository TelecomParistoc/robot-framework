GENERIC_ROBOT_PREFIX = framework/robot/
BIG_ROBOT = framework/local_robot/big_robot.py
PYTHON_PREFIX = /usr/local/lib/python2.7/dist-packages/



.PHONY: install


install:
	cd callbacks_python && make install
	cd rpi_gpio && make install
	cp -a $(GENERIC_ROBOT_PREFIX)*.py $(PYTHON_PREFIX)
	cp $(BIG_ROBOT) $(PYTHON_PREFIX)





GENERIC_ROBOT_PREFIX = framework/robot/
ACTION_PREFIX = framework/action/
BIG_ROBOT = framework/local_robot/big_robot.py
PYTHON_PREFIX = /usr/local/lib/python3.5/dist-packages/



.PHONY: install


install:
	cd callbacks_python && make install
	cd rpi_gpio && make install
	mkdir -p $(PYHON_PREFIX)
	cp -a $(GENERIC_ROBOT_PREFIX)*.py $(PYTHON_PREFIX)
	cp -a $(ACTION_PREFIX)*.py $(PYTHON_PREFIX)
	cp $(BIG_ROBOT) $(PYTHON_PREFIX)





TARGET = libGPIO.so
SRCS = gpio.cpp gpio_thread.cpp
PREFIX = /usr/local/lib/

PYTHON_EXE = gpio_test.py
PYTHON_BINDING = python_binding.py
PYTHON_UTILS = gpio_lib_path
PYTHON_PREFIX = /usr/local/lib/python2.7/dist-packages/
LOCAL_PYTHON = gpio.py
LOCAL_PYTHON_UTILS =

CC = g++
CFLAGS = -O2 -std=c++11 -Wall -Werror -fpic
LDFLAGS = -lwiringPi -shared

.PHONY: all test clean


all: $(TARGET)

%.so: $(SRCS)
	$(CC) $(CFLAGS) -o $@ $(SRCS) $(LDFLAGS)

test: $(TARGET)
	python $(PYTHON_EXE)

install: $(TARGET)
	cp $(PYTHON_BINDING) $(PYTHON_PREFIX)$(LOCAL_PYTHON)
	sudo python -c 'f = open("$(PYTHON_PREFIX)$(LOCAL_PYTHON)", "r+"); content = f.read().replace("LIBNAME", "'$(PREFIX)$(TARGET)'"); f.write(content)';
	mkdir -p $(PREFIX)
	cp $(TARGET) $(PREFIX)
	chmod 0755 $(PREFIX)/$(TARGET)
	ldconfig
	ldconfig -p | grep GPIO

clean:
	rm -f $(TARGET)
	rm -f *.pyc

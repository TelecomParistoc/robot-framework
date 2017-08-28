TARGET = libGPIO.so
SRCS = gpio.cpp gpio_thread.cpp
PREFIX = /usr/local/lib

PYTHON_EXE = gpio_test.py
PYTHON_BINDING = python_binding.py
LOCAL_PYTHON = /usr/local/lib/python2.7/dist-packages/gpio.py

CC = g++
CFLAGS = -O2 -std=c++11 -Wall -Werror -fpic
LDFLAGS = -shared

.PHONY: all test clean


all: test

%.so: $(SRCS)
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

test: $(TARGET)
	python $(PYTHON_EXE)

install: $(TARGET)
	cp $(PYTHON_BINDING) $(LOCAL_PYTHON)
	mkdir -p $(PREFIX)
	cp $(TARGET) $(PREFIX)
	chmod 0755 $(PREFIX)/lib/$(TARGET)
	ldconfig
	ldconfig -p | grep GPIO

clean:
	rm -f $(TARGET)
	rm -f *.pyc

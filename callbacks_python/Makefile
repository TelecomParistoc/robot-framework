TARGET = timer_callbacks_test.so
SRCS = timer_callbacks_test.cpp
PYTHON_EXE = timer_callbacks_test.py
PYTHON_LIB = encapsulate_callback.py
LOCAL_PYTHON = /usr/local/lib/python3.5/dist-packages/


CC = g++
CFLAGS = -O2 -std=c++11 -Wall -Werror -fpic
LDFLAGS = -shared

.PHONY: all test clean


all: test

%.so: %.cpp
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

test: $(TARGET)
	python $(PYTHON_EXE)

install:
	cp $(PYTHON_LIB) $(LOCAL_PYTHON)

clean:
	rm -f $(TARGET)
	rm -f *.pyc

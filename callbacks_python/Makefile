TARGET = timer_callbacks_test.so
SRCS = timer_callbacks_test.cpp
PYTHON_EXE = timer_callbacks_test.py


CC = g++
CFLAGS = -O2 -std=c++11 -Wall -Werror -fpic
LDFLAGS = -shared

.PHONY: all test clean


all: test

%.so: %.cpp
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

test: $(TARGET)
	python $(PYTHON_EXE)

clean:
	rm -f $(TARGET)

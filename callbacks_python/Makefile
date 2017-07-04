TARGET = libpython_callback.so
SRCS = python_callback.c
HEADERS = $(addprefix ./, ${SRCS:.c=.h})
OBJECTS = $(addprefix build/,${SRCS:.c=.o})

TESTS = tests/timer_callbacks_test.so
TESTS_PYTHON = tests/timer_callbacks_test.py

CC = gcc
CFLAGS = -O2 -std=gnu99 -I/usr/include/python2.7 -Wall -Werror -fpic
LDFLAGS= -shared

PREFIX = /usr/local
VPATH = build/ tests/


.PHONY: all build clean install tests


all: build build/$(TARGET)

build:
	@mkdir -p build

build/%.o: %.c build/%.d
	@echo "$<"
	@$(CC) -c -o $@ $< $(CFLAGS)

build/%.d: %.c
	@$(CC) $(CFLAGS) -MM -MF $@ -MP $<

build/$(TARGET): $(OBJECTS)
	@echo "Linking target $@"
	@$(CC) $(CFLAGS) $(OBJECTS) -o $@ $(LDFLAGS)


tests/%.so: tests/%.cpp
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

tests: CC=g++
tests: LDFLAGS=-lpython_callback -lpython2.7 -shared
tests: CFLAGS=-O2 -std=c++11 -I/usr/include/python2.7 -Wall -Werror -fpic
tests: $(TESTS) $(TESTS_PYTHON)

$(TESTS_PYTHON):
	python $(TESTS_PYTHON)


clean:
	rm -rf build
	rm -f $(TESTS)

install: build/$(TARGET)
	mkdir -p $(DESTDIR)$(PREFIX)/lib
	mkdir -p $(DESTDIR)$(PREFIX)/include/python_callback
	cp build/$(TARGET) $(DESTDIR)$(PREFIX)/lib/
	cp $(HEADERS) $(DESTDIR)$(PREFIX)/include/python_callback/
	chmod 0755 $(DESTDIR)$(PREFIX)/lib/$(TARGET)
	ldconfig
	ldconfig -p | grep python_callback

-include $(subst .c,.d, $(SRCS))

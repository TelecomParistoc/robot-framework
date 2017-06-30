TARGET = libAX12.so
SRCS = python_callback.c
HEADERS = $(addprefix ./, ${SRCS:.c=.h})
OBJECTS = $(addprefix build/,${SRCS:.c=.o})

CC = gcc
CFLAGS = -O2 -std=gnu99 -Wall -Werror -fpic
LDFLAGS= -shared

PREFIX = /usr/local
VPATH = build/


.PHONY: all build clean tests AX12console jsinstall

all: build build/$(TARGET)

build:
	@mkdir -p build

build/%.o: %.c build/%.d
	@echo "$<"
	@$(CC) -c -o $@ $< $(CFLAGS)

build/%.d : %.c
	@$(CC) $(CFLAGS) -MM -MF $@ -MP $<

build/$(TARGET): $(OBJECTS)
	@echo "Linking target $@"
	@$(CC) $(CFLAGS) $(OBJECTS) -o $@ $(LDFLAGS)

clean:
	rm -f build/*.o build/*.so build/*.d
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

CC = g++

TARGET = robot_loop_starter
LOOPING_SERVICE = launch.py

$(TARGET): loop_launch_check_button_state.cpp
	$(CC) -o $@ $^

install: $(TARGET)
	chmod u+x setup.sh
	./setup.sh `pwd`/$(TARGET) `pwd`/$(LOOPING_SERVICE) `pwd`/program_and_commands.config /var/robot_config/program_path /var/robot_config/commands
	@rm -rf `pwd`/$(TARGET)

clean:
	@rm -rf `pwd`/$(TARGET)

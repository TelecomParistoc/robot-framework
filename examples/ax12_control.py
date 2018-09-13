from AX12 import AX12

# Using the AX12 with ID 25
motor = AX12(25)

# Turning the AX12 to position 100 degrees
motor.move(100)

sleep(2)

# Rotating the AX12 at speed 50 (speeds are between -100 and 100)
motor.turn(50)

sleep(2)

# Stopping the AX12
motor.turn(0)

import sys

def stop(motor):
    stopped = False

    while not stopped:
        try:
            motor.turn(0)
            stopped = True
        except:
            pass

for i in sys.argv:
    motor = AX12(i)
    stop(motor)

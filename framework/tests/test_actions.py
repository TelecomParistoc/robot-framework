from action import Sequence, Function, ThreadedFunction, AX12MoveAction
from time import sleep
from AX12 import AX12

mot1 = AX12(142)
mot2 = AX12(146)
mot1.set_speed(20)
mot2.set_speed(20)
mot1.set_torque(20)

def f(a):
    print("function ", a)

def c(a):
    print("callback ", a)

main = Sequence("main", lambda: c("main"))

main.add_actions([AX12MoveAction(mot1, 0).wait(),
                  AX12MoveAction(mot1, 150, 0).wait(2)])
main.wait()
main.exec()

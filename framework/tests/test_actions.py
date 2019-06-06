from AX12simu import AX12_simu

from action import Sequence, Function, ThreadedFunction
from time import sleep

ax = AX12_simu(1, response_time=2)

def f(a):
    print("function ", a)

def c(a):
    print("callback ", a)

# Main sequence, composed of the subsequence s1 and the action a2
main = Sequence(lambda: c("main"), "main")

# Subsequence s1, composed of two actions a11 and a12
s1  = Sequence(lambda: c("s1"), "s1")
a11 = Function(ax.move, [5])
a12 = Function(f, ["a12"], None)
s1.add_actions([a11, a12]).wait()

# Action a2
a2 = ThreadedFunction(f, ["a2"], None)

main.add_actions([s1,a2])

main.exec()

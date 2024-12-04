from z3 import *

x_0 = BitVec('x_0', 32)
x_1 = BitVec('x_1', 32)
x_2 = BitVec('x_2', 32)

x_2 = x_1

x_6 = BitVec('x_6', 32)
x_9 = BitVec('x_9', 32)
x_10 = BitVec('x_10', 32)
for index in range(1, 5):
    x_6 = index
    if x_6 >= 5:
        break

    x_9 = index
    x_10 = x_2 + x_9
    x_2 = x_10

x_0 = x_2

solver = Solver()
solver.add(x_0 == 30)
if solver.check() == sat:
    model = solver.model()
    print('x_1 ---> ', model)
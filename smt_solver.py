from z3 import *

x = Real('x')

s = Solver()
s.add(x * x + 5 == 11.25)

while s.check() == sat:
    res = s.model()
    print("Res: x = ", res.evaluate(x))
    s.add(x != res.evaluate(x))
from z3 import *

x = Real('x')

s = Solver()
s.add(x * x + 5 == 11.25)

while s.check() == sat:
    res = s.model()[x]
    print("Res: x = ", str(res))
    s.add(x != res)
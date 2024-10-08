from z3 import *

p, q = Bools('p q')
solve(And(p, Not(q)))

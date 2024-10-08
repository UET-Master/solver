from z3 import *

p, q = Bools('p q')
solve(And(Or (p, q), Or(p, Not(q))))

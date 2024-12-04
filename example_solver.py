from z3 import *

p, q = Bools('p q')
solve(And(Or (p, q), Or(p, Not(q))))

a = BitVecVal(-2, 16)
b = BitVecVal(65534, 16)
print (simplify(a == b))

X = IntVector('x', 5)
Y = RealVector('y', 5)
P = BoolVector('p', 5)
print (X)
print (Y)
print (P)
print ([ y**2 for y in Y ])
print (Sum([ y**2 for y in Y ]))

x = Int('x')
y = Int('y')
print (simplify(x + y + 2*x + 3))
print (simplify(x < y + x + 2))

x = Real('x')
solve(3*x == 1)

set_option(rational_to_decimal=True)
solve(3*x == 1)

set_option(precision=30)
solve(3*x == 1)

x = Real('x')
y = Real('y')
solve(x**2 + y**2 == 3, x**3 == 2)

set_option(precision=3)
print ("Solving, and displaying result with 3 decimal places")
solve(x**2 + y**2 == 3, x**3 == 2)

x = Real('x')
print (x + 1/3)
print (x + Q(1,3))
print (x + "1/3")
print (x + 0.25)

x = Real('x')
solve(x > 4, x < 0)

p = Bool('p')
q = Bool('q')
print (And(p, q, True))
print (simplify(And(p, q, True)))
print (simplify(And(p, False)))

p = Bool('p')
q = Bool('q')
r = Bool('r')
solve(Implies(p, q), r == Not(q), Or(Not(p), r))

x = BitVec('x', 16)
y = BitVec('y', 16)
print (x + 2)
# Internal representation
print ((x + 2).sexpr())

# -1 is equal to 65535 for 16-bit integers 
print (simplify(x + y - 1))

x = Int('x')
y = Int('y')
f = Function('f', IntSort(), IntSort())
solve(f(f(x)) == x, f(x) == y, x != y)

x = Int('x')
y = Int('y')
f = Function('f', IntSort(), IntSort())
s = Solver()
s.add(f(f(x)) == x, f(x) == y, x != y)
print (s.check())
m = s.model()
print ("f(f(x)) =", m.evaluate(f(f(x))))
print ("f(x)    =", m.evaluate(f(x)))

# Define two integer variables
x = Int('x')
y = Int('y')

# Create a solver
solver = Solver()

# Add constraints: x + y = 10 and x > y
solver.add(x + y == 10, x > y)

print("Solver: ", solver)

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()  # Get the model (solution)
    
    # Evaluate the values of x and y in the model
    x_val = model.eval(x)
    y_val = model.eval(y)

    print(f"Solution: x = {x_val}, y = {y_val}")
else:
    print("No solution")


positive = BitVecVal(42.67, 8)  # Positive 42
negative = BitVecVal(-42, 8) # Negative -42 (two's complement)

print("Positive value:", positive)
print("Negative value:", negative)

# Define symbolic variables
_1 = Int('_1')  # Input value
_2 = Int('_2')  # Copy of _1
start = Int('start')  # Start of the range
end = Int('end')  # End of the range
_4 = Array('_4', IntSort(), IntSort())  # Array to represent the range
_3 = Int('_3')  # Iterator index (current position in the range)

# Define solver
solver = Solver()

# Constraints for `_2 = copy _1`
solver.add(_2 == _1)

# Constraints for `_4 = Range { start: 1, end: 5 }`
solver.add(start == 1)  # Start of the range
solver.add(end == 5)    # End of the range

# Represent the range `_4` as an array of indices
solver.add(ForAll([_3], Implies(And(_3 >= start, _3 < end), _4[_3] == _3)))
solver.add(ForAll([_3], Implies(Or(_3 < start, _3 >= end), _4[_3] == 0)))  # Outside range -> invalid

# Constraints for iterator initialization
# `_3` starts at the beginning of the range
solver.add(_3 == start)

# Check the constraints
if solver.check() == sat:
    print("Constraints are satisfiable!")
    print("Model:")
    model = solver.model()
    print(model)
else:
    print("Constraints are unsatisfiable!")

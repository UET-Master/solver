from z3 import *

sudoku_instance = ((0,0,0,0,9,4,0,3,0),
                   (0,0,0,5,1,0,0,0,7),
                   (0,8,9,0,0,0,0,4,0),
                   (0,0,0,0,0,0,2,0,8),
                   (0,6,0,2,0,1,0,5,0),
                   (1,0,2,0,0,0,0,0,0),
                   (0,7,0,0,0,0,5,2,0),
                   (9,0,0,0,6,5,0,0,0),
                   (0,4,0,9,8,0,0,0,0))


# 9 x 9 matrix of sudoku
matrix = [[Int("x_%s_%s" % (i + 1, j + 1)) for j in range(9)] for i in range(9)]

# Each cell contains a value in range(9)
cell_constraint = [And(matrix[i][j] >= 1, matrix[i][j] <= 9) for i in range(9) for j in range(9)]

# Each row contains a digit at most once
row_constraint = [Distinct(matrix[i]) for i in range(9)]

# Each column contains a digit at most once
column_constraint = [Distinct([matrix[i][j] for i in range(9)]) for j in range(9)]

# Each 3x3 square contains a digit at most once
square_constraint = [Distinct([matrix[i0 * 3 + i][j0 * 3 + j] for i in range(3) for j in range(3)]) for i0 in range(3) for j0 in range(3)]

maxtrix_constraint = cell_constraint + row_constraint + column_constraint + square_constraint

# If the value at sudoku_instance[i][j] is not empty, the matrix[i][j] must match the given value in sudoku_instance[i][j]
instance_contraint = [If(sudoku_instance[i][j] == 0, True, matrix[i][j] == sudoku_instance[i][j]) for i in range(9) for j in range(9)]

solver = Solver()
solver.add(maxtrix_constraint + instance_contraint)
if solver.check() == sat:
    model = solver.model()
    print('Model --> ', model)
    res = [[model.evaluate(matrix[i][j]) for j in range(9)] for i in range(9)]
    print_matrix(res)
else:
    print ("The given sudoku is not solved")



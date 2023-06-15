from utils.parser_utils import Context
from utils.primitives import Matrix


# General functions
def pretty_print(ctx: Context, args):
    """
    If the ``pretty_print`` variable is set to true, this will attempt to output arguments
    nicely. For example, it makes matrices more readable. Otherwise, it has normal Python
    behavior.
    :param ctx: the context
    :param args: the arguments
    """
    if len(args) > 1 or len(args) == 0 or not ctx.variables()["pretty_print"]:
        print(*args)
    elif isinstance(args[0], Matrix):
        elements = sum(args[0].matrix, [])
        column_size = len(args[0].columns())
        largest_strings = [max([len(str(element)) for element in column]) for column in args[0].columns()]

        print("[ ", end="")
        current = 1
        for element in elements:
            if current > column_size:
                current -= column_size
                print()
                print("  ", end="")
            print(str(element) + (1 + largest_strings[current - 1] - len(str(element))) * " ", end="")
            current += 1
        print("]")
    else:
        print(*args)


# Matrix functions
def transpose(matrix: Matrix):
    return Matrix(matrix.columns())


def det(matrix: Matrix):
    # TODO Only allow square matrices but make a good error system for it first
    # TODO Make this faster
    if len(matrix.matrix) == 1:
        return matrix.matrix[0][0]

    determinant = 0
    # We develop the first row, following the Leibniz formula
    for j in range(1, len(matrix.matrix) + 1):
        determinant += (-1) ** (1 + j) * matrix.matrix[0][j - 1] * det(submatrix(matrix, 1, j))
    return determinant


def inv(matrix: Matrix):
    # TODO Only allow square matrices
    # TODO Make this faster as well
    pass


def trace(matrix: Matrix):
    # TODO Only support square matrices, but create a good error system for it first
    return sum([matrix.matrix[i][i] for i in range(len(matrix.matrix))])


def diagonal(elements: Matrix):
    """
    Constructs a matrix with the elements of this row or column vector on the diagonal.
    :param elements: the row or column vector
    :return: a diagonal matrix
    """
    # TODO Add any vector support
    return Matrix([[elements.matrix[0][i] if i == j else 0 for j in range(len(elements.matrix[0]))] for i in range(len(elements.matrix[0]))])


def eye(size):
    return Matrix([[1 if i == j else 0 for j in range(size)] for i in range(size)])


def submatrix(matrix, row_number, column_number):
    """
    :param matrix: the matrix
    :param row_number: the row
    :param column_number: the column
    :return: the matrix with the given row and column removed
    """
    remaining_rows = []
    for i, row in enumerate(matrix.rows()):
        if i + 1 != row_number:
            remaining_rows.append(row)
    remaining_columns = []
    for i, column in enumerate(Matrix(remaining_rows).columns()):
        if i + 1 != column_number:
            remaining_columns.append(column)
    return transpose(Matrix(remaining_columns))


def reduced_echelon_form(matrix: Matrix):
    pass

import numpy as np

from utils.primitives import *


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
        elements = sum(args[0].rows(), [])
        column_size = args[0].shape()[1]
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


# Number functions
def minimum(value: Matrix):
    # TODO Add preconditions
    # TODO Add row/column-specific extremes
    return min(value.vector())


def maximum(value: Matrix):
    # TODO Add preconditions
    # TODO Add row/column-specific extremes
    return max(value.vector())


# Matrix functions
def transpose(matrix: Matrix):
    # TODO Add preconditions
    return Matrix(matrix.array.transpose())


def determinant(matrix: Matrix):
    # TODO Add preconditions
    # TODO Add postconditions (general rounding system)
    return round(np.linalg.det(matrix.array), 6)


def inverse(matrix: Matrix):
    # TODO Add preconditions
    return matrix ** -1


def trace(matrix: Matrix):
    # TODO Add preconditions
    # Trace function gives an array back
    return matrix.array.trace()[0, 0]


def diagonal(vector: Matrix):
    """
    Constructs a matrix with the elements of this row or column vector on the diagonal.
    :param vector: the row or column vector
    :return: a diagonal matrix
    """
    # TODO Add preconditions
    return Matrix(np.diag(vector.vector()))


def eye(size):
    # TODO Add preconditions
    return Matrix(np.identity(size, int))


def dot(left: Matrix, right: Matrix):
    # TODO Add preconditions
    return np.dot(left.vector(), right.vector())


def cross(left: Matrix, right: Matrix):
    # TODO Add preconditions
    return np.cross(left.vector(), right.vector())

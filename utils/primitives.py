import numbers
from typing import Literal

import numpy as np
from utils.parser_utils import Context


class Matrix:
    array: np.ndarray

    def __init__(self, matrix=None):
        """
        Creates a matrix from a given object, depending on the type it creates:

        - an empty matrix if ``None``,
        - a non-referencing copy if a Matrix,
        - a row matrix for Slices,
        - a row matrix for lists with single elements,
        - a matrix for lists of lists with single elements,
        - a non-referencing copy for Numpy arrays, or
        - a matrix with one element for single elements.
        :param matrix: the object
        """
        if matrix is None:
            self.array = np.matrix([[]])
        elif isinstance(matrix, Matrix):
            self.array = matrix.array.copy()
        elif isinstance(matrix, Slice):
            # This turns a slice into a list
            # TODO Add preconditions (check if start AND stop exist)
            self.array = np.array([list(range(matrix.stop)[matrix.slice()])])
        elif isinstance(matrix, list):
            if len(matrix) == 0 or not isinstance(matrix[0], list):
                # Matrix is a list, but not 2-dimensional
                self.array = np.array([matrix])
            else:
                self.array = np.array(matrix)
        elif isinstance(matrix, np.ndarray):
            if len(matrix.shape) != 2:
                # Matrix is Numpy array, but not 2-dimensional
                self.array = np.array([matrix.tolist()])
            else:
                # Matrix is already a Numpy array
                self.array = matrix.copy()
        else:
            # Matrix is a single value
            self.array = np.array([[matrix]])

    def execute(self, _, args):
        args = self._transform_keys(args)

        # Fetching the values
        if len(args) == 1:
            if self.array.shape[0] == 1:
                # If there's only one row, return the column element
                result = self.array[0, args[0]]
            elif self.array.shape[1] == 1:
                # Otherwise, if there's only one column, return the row element
                result = self.array[args[0], 0]
            else:
                # Otherwise, return the full row
                result = self.array[args[0]]
        elif len(args) == 2:
            # We need to manually make a column vector out of this, since Numpy just returns a list
            result = self.array[args[0], args[1]]
        else:
            raise RuntimeError(f"Too many arguments: expected 2 or lower arguments, but found {len(args)}")

        # Making sure the result is a valid type
        if Matrix(result).shape() != (1, 1):
            return Matrix(result)
        else:
            # The result is a singular value and can be unpacked
            return result

    def arguments_needed(self):
        # TODO Find another solution for this, possibly implementing a '[]' operator
        return 0

    def shape(self):
        """
        Returns a tuple containing the size of respectively the rows and columns.
        :return: the shape of this matrix
        """
        return self.array.shape

    def rows(self):
        """
        Returns a list with all the rows of this matrix
        :return: a list of the rows
        """
        return self.array.tolist()

    def columns(self):
        """
        Returns a list with all the columns of this matrix.
        :return: a list of the columns
        """
        return self.array.transpose().tolist()

    def vector(self) -> list:
        """
        Returns a list with all the elements of this matrix
        :return: a list with all the elements
        """
        return [item for sublist in self.array.tolist() for item in sublist]

    def concat(self, other, dimension: Literal[0, 1] = 0):
        """
        Adds the vectors to this matrix, either as rows (``dimension`` is 0) or as columns (``dimension``
        is 1). The vectors must all be of the same size and must match the size of the array.
        If the vector is a single value and not a sequence, it will be converted to one.
        :param other: the vectors, or a single value
        :param dimension: whether to add the vectors as rows (0, default) or as columns (1)
        """
        # TODO Add preconditions
        if not isinstance(other, list):
            other = [[other]]

        # If the matrix is empty, we can just create a new one.
        if len(self) == 0:
            self.array = Matrix(other).array
            return

        self.array = (np.vstack if dimension == 0 else np.hstack)([self.array, np.matrix(other)])

    def __delitem__(self, key):
        # TODO Add preconditions
        key = self._transform_keys(key)

        # Deleting the values
        if len(key) == 1:
            if self.array.shape[0] == 1:
                # If there's only one row, delete the column element
                self.array = np.delete(self.array, key[0], 1)
            elif self.array.shape[1] == 1:
                # Otherwise, if there's only one column, delete the row element
                self.array = np.delete(self.array, key[0], 0)
            else:
                # Otherwise, delete the full row
                self.array = np.delete(self.array, key[0], 0)
        elif len(key) == 2:
            # We need to delete the rows and columns manually, since Numpy works differently
            self.array = np.delete(np.delete(self.array, key[0], 0), key[1], 1)
        else:
            raise RuntimeError(f"Too many arguments: expected 2 or lower arguments, but found {len(key)}")

    def __getitem__(self, item):
        return self.execute(None, list(item))

    def __setitem__(self, key, value):
        # TODO Add preconditions
        # TODO When manipulating arrays, use only arrays and not lists, singular values and arrays inconsistently
        key = self._transform_keys(key)

        # Setting the values
        if len(key) == 1:
            if self.array.shape[0] == 1:
                # If there's only one row, change the element in that row
                self.array[0, key[0]] = value
            elif self.array.shape[1] == 1:
                # Otherwise, if there's only one column, change the element in that column
                self.array[key[0], 0] = value
            else:
                # Otherwise, change the full row
                # The value is a matrix now
                # TODO Add preconditions for this particular case
                self.array[key[0]] = value.array
        elif len(key) == 2:
            # TODO Make a function for transforming
            if isinstance(value, Matrix):
                # TODO Add preconditions to only make it possible if the value is the same shape as the queried key
                value = value.array
            elif isinstance(value, Slice):
                # Makes a list out of this slice
                value = list(range(value.stop)[value.slice()])
            self.array[key[0], key[1]] = value
        else:
            raise RuntimeError(f"Too many arguments: expected 2 or lower arguments, but found {len(key)}")

    def __add__(self, other):
        # Scalar addition
        if isinstance(other, numbers.Number):
            return Matrix(self.array + other)

        # Matrix addition
        if self.array.shape != other.array.shape:
            raise RuntimeError(f"Cannot add matrices with different dimensions")
        return Matrix(self.array + other.array)

    def __sub__(self, other):
        # Scalar subtraction
        if isinstance(other, numbers.Number):
            return Matrix(self.array - other)

        # Matrix subtraction
        if self.array.shape != other.array.shape:
            raise RuntimeError(f"Cannot subtract matrices with different dimensions")
        return Matrix(self.array - other.array)

    def __mul__(self, other):
        # Scalar multiplication
        if isinstance(other, numbers.Number):
            return Matrix(self.array * other)

        # Matrix multiplication
        # TODO Add preconditions
        return Matrix(self.array @ other.array)

    def __pow__(self, power, modulo=None):
        # TODO Implement checks for optimized powers, for example when multiplying with the identity matrix
        # TODO Add preconditions
        if int(power) != power:
            raise RuntimeError("The exponent of a matrix should be a whole number")

        if power == 1:
            return Matrix(self)
        elif power > 0:
            original = self.array.copy()
        elif power == 0:
            return Matrix(np.identity(self.array.shape[0], dtype=int))
        else:
            original = np.linalg.inv(self.array)
            power *= -1

        result = original.copy()
        while power > 1:
            result @= original
            power -= 1
        return Matrix(result.round(6))

    def __contains__(self, item):
        # TODO Add preconditions
        # TODO Add support for row/column vectors
        return item in self.vector()

    def __len__(self):
        # TODO Add support for dimensions
        return len(self.vector())

    def __copy__(self):
        return Matrix(self)

    def __str__(self):
        return "[" + "; ".join([", ".join([str(element) for element in row]) for row in self.array.tolist()]) + "]"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _transform_keys(keys) -> list:
        """
        When querying a Matrix, this function can transform the key argument into
        Python primitives. It also takes both finite and infinite Slices into account.
        :param keys: the keys
        :return: a list of Python primitive, supported keys
        """
        result = []
        for key in keys:
            if isinstance(key, Slice):
                result.append(key.slice())
            elif isinstance(key, Matrix):
                # TODO Add preconditions (only vectors allowed)
                result.append(key.vector())
            else:
                result.append(key)
        return result


class Slice:
    def __init__(self, start, stop, step=1):
        self.start = start
        self.stop = stop
        self.step = step

    def slice(self):
        return slice(self.start, self.stop, self.step)

    def indices(self, length):
        return self.slice().indices(length)

    def __add__(self, other):
        return Slice(self.start + other if self.start is not None else None,
                     self.stop + other if self.stop is not None else None,
                     self.step)

    def __sub__(self, other):
        return Slice(self.start - other if self.start is not None else None,
                     self.stop - other if self.stop is not None else None,
                     self.step)

    def __str__(self):
        result = ""
        if self.start is not None:
            result += str(self.start) + " "
        result += ":"
        if self.stop is not None:
            result += " " + str(self.stop)
        if self.step is not None and self.step != 1:
            result += " : " + str(self.step)
        return result

    def __repr__(self):
        return self.__str__()


class Function:
    def __init__(self, parameters, block, curried=None, infix=False):
        self.parameters = parameters
        self.block = block
        self.curried = [] if curried is None else curried
        self.infix = infix

    def execute(self, ctx: Context, args):
        if len(self.parameters) < len(self.curried) + len(args):
            raise RuntimeError(
                f"Too many arguments: expected {len(self.parameters)} arguments, but found {len(self.curried) + len(args)}")

        for i, parameter in enumerate(self.parameters):
            ctx.variables()[parameter] = self.curried[i] if i < len(self.curried) else args[i - len(self.curried)]

        from elements.statements import run_statements
        run_statements(self.block, ctx)
        returned = self.block.returned
        self.block.clear(ctx)

        return returned

    def arguments_needed(self):
        return len(self.parameters) - len(self.curried)

    def __str__(self):
        return ("infix " if self.infix else "") + f'fn({", ".join(self.parameters)})'

    def __repr__(self):
        return self.__str__()


class PythonFunction(Function):
    def __init__(self, python_function, infix=False):
        super().__init__([], None, infix=infix)
        self.python_function = python_function

    def execute(self, ctx, args):
        return self.python_function(*args)

    def arguments_needed(self):
        # We don't want to enable currying for built-in Python functions!
        return 0

    def __str__(self):
        return f'built-in fn()'


class ContextFunction(Function):
    def __init__(self, context_function):
        super().__init__([], None)
        self.context_function = context_function

    def execute(self, ctx, args):
        return self.context_function(ctx, args)

    def arguments_needed(self):
        # TODO Find another system for this
        # We don't want to enable currying for built-in Python functions!
        return 0

    def __str__(self):
        return f'built-in fn()'


from utils.parser_utils import Context


class Matrix:
    def __init__(self, matrix=None):
        self.matrix = [[]] if matrix is None else matrix

    def execute(self, ctx: Context, args):
        if len(args) == 1:
            # If there's only one row, we want to return the column
            if len(self.matrix) == 1:
                return self.matrix[0][args[0] + 1]
            else:
                return self.matrix[args[0] + 1]
        elif len(args) == 2:
            return self.matrix[args[0] + 1][args[1] + 1]
        else:
            raise RuntimeError(f"Too many arguments: expected 2 or lower arguments, but found {len(args)}")

    def arguments_needed(self):
        return 0

    def rows(self):
        return self.matrix

    def columns(self):
        return [[row[i] for row in self.matrix] for i in range(len(self.matrix[0]))]

    def add_row(self, row):
        if len(row) != len(self.matrix[0]):
            raise RuntimeError(f"You cannot add a row of length {len(row)} to a matrix with {len(self.matrix[0])} columns")
        self.matrix.append(row)

    def add_column(self, column):
        """
        Adds a column to this matrix. Note that the column itself is just a list, not a matrix.
        :param column: the elements of this column
        """
        if len(column) != len(self.matrix):
            raise RuntimeError(f"You cannot add a column of length {len(column)} to a matrix with {len(self.matrix)} rows")

        new = []
        for i, row in enumerate(self.matrix):
            new.append(row + [column[i]])
        self.matrix = new

    def dimensions_match(self, other: 'Matrix'):
        return len(self.matrix) == len(other.matrix) and len(self.matrix[0]) == len(other.matrix[0])

    def is_square_matrix(self):
        return len(self.matrix) == len(self.matrix[0])

    def __add__(self, other: 'Matrix'):
        if not self.dimensions_match(other):
            raise RuntimeError(f"Cannot add matrices with different dimensions")
        return Matrix([[self.matrix[i][j] + other.matrix[i][j] for j in range(len(self.matrix[i]))] for i in range(len(self.matrix))])

    def __sub__(self, other: 'Matrix'):
        if not self.dimensions_match(other):
            raise RuntimeError(f"Cannot subtract matrices with different dimensions")
        return Matrix([[self.matrix[i][j] - other.matrix[i][j] for j in range(len(self.matrix[i]))] for i in range(len(self.matrix))])

    def __mul__(self, other):
        # Scalar multiplication
        if isinstance(other, float) or isinstance(other, int):
            return Matrix([[self.matrix[i][j] * other for j in range(len(self.matrix[i]))] for i in range(len(self.matrix))])

        # Matrix multiplication
        if len(self.columns()) != len(other.rows()):
            raise RuntimeError("Cannot multiply matrices with non-matching dimensions")
        result = [[None for j in range(len(other.matrix[0]))] for i in range(len(self.matrix))]
        for i in range(len(self.matrix)):
            for j in range(len(other.matrix[0])):
                result[i][j] = sum([self.rows()[i][k] * other.columns()[j][k] for k in range(len(other.matrix))])
        return Matrix(result)

    def __pow__(self, power, modulo=None):
        # TODO Implement checks for optimized powers, for example when multiplying with the identity matrix
        # TODO Implement negative powers and any number powers (?)
        if not self.is_square_matrix():
            raise RuntimeError("Only square matrices have powers")
        elif power < 0 or int(power) != power:
            raise RuntimeError("The exponent of a matrix should be a natural number")
        elif power == 0:
            from utils.builtins import eye
            return eye(len(self.matrix))

        result = self
        while power > 1:
            result *= self
            power -= 1
        return result

    def __str__(self):
        return "[" + "; ".join([", ".join([str(element) for element in row]) for row in self.matrix]) + "]"

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
    def __init__(self, python_function):
        super().__init__([], None)
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
        # We don't want to enable currying for built-in Python functions!
        return 0

    def __str__(self):
        return f'built-in fn()'


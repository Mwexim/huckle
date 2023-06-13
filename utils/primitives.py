from utils.parser_utils import Context


class Matrix:
    def __init__(self, matrix=None):
        self.matrix = [[]] if matrix is None else matrix

    def execute(self, ctx: Context, args):
        if len(args) == 1:
            # If there's only one row, we want to return the column
            if len(self.matrix) == 1:
                return self.matrix[0][args[0]]
            else:
                return self.matrix[args[0]]
        elif len(args) == 2:
            return self.matrix[args[0]][args[1]]
        else:
            raise RuntimeError(f"Too many arguments: expected 2 or lower arguments, but found {len(args)}")

    def arguments_needed(self):
        return 0

    def rows(self):
        return self.matrix

    def columns(self):
        return [[row[i] for row in self.matrix] for i in range(len(self.matrix[0]))]

    def __add__(self, other: 'Matrix'):
        if len(self.rows()) == len(other.rows()):
            # If the rows match, we add as column
            matrix = Matrix(self.matrix)
            for column in other.columns():
                matrix.add_column(column)
            return matrix
        elif len(self.columns()) == len(other.columns()):
            return Matrix(self.matrix + other.matrix)
        else:
            raise RuntimeError("The dimensions of these matrices do not match to add.")

    def add_row(self, row):
        self.matrix + row

    def add_column(self, column):
        """
        Adds a column to this matrix. Note that the column itself is just a list, not a matrix.
        :param column: the elements of this column
        """
        new = []
        for i, row in enumerate(self.matrix):
            new.append(row + [column[i]])
        self.matrix = new

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

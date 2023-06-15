from utils.parser_utils import Context
from utils.primitives import Function, Matrix


class Expression:
    def evaluate(self, ctx: Context):
        raise NotImplementedError("This method should be implemented")


class Primitive(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self, ctx: Context):
        return self.value


class NestedExpression(Expression):
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, ctx: Context):
        return self.expr.evaluate(ctx)


class MatrixExpression(Expression):
    def __init__(self, last_operation=None):
        self.last_operation = last_operation

    def evaluate(self, ctx: Context):
        if self.last_operation is None:
            return Matrix()
        else:
            result = self.last_operation.evaluate(ctx)
        # Check if the dimensions are right.
        lengths = [len(row) for row in result.matrix]
        if len(lengths) > 1 and not lengths.count(lengths[0]) == len(lengths):
            raise RuntimeError(f"The matrix does not conform to its dimensions")
        return result


class UnitMatrixExpression(Expression):
    def __init__(self, expression):
        self.expression = expression

    def evaluate(self, ctx: Context):
        result = self.expression.evaluate(ctx)
        if isinstance(result, Matrix):
            # We copy the matrix because it cannot be mutated because of its reference!
            return Matrix(list(result.matrix))
        else:
            return Matrix([[self.expression.evaluate(ctx)]])


class MatrixOperation(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, ctx: Context):
        left = self.left.evaluate(ctx)
        right = self.right.evaluate(ctx)
        match self.op:
            case ",":
                # Add element to row or add column vector to matrix
                if isinstance(right, Matrix):
                    for column in right.columns():
                        left.add_column(column)
                else:
                    left.add_column([right])
            case ";":
                # Add element to new row or add row vector to matrix
                if isinstance(right, Matrix):
                    for row in right.rows():
                        left.add_row(row)
                else:
                    left.add_row([right])
        return left


class UnaryOperator(Expression):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, ctx: Context):
        expr = self.expr.evaluate(ctx)
        match self.op:
            case "-":
                return -expr
            case "not":
                return not expr


class BinaryOperator(Expression):
    def __init__(self, left, op, right, commutative=True):
        self.left = left
        self.op = op
        self.right = right
        self.commutative = commutative

    def evaluate(self, ctx: Context):
        left = self.left.evaluate(ctx)
        right = self.right.evaluate(ctx)
        try:
            result = self.calculate(left, self.op, right)
            return result
        except:
            # Sometimes, we only want to define operations on one type.
            # An example is the matrix multiplication with a scalar.
            if self.commutative:
                result = self.calculate(right, self.op, left)
                return result

    @staticmethod
    def calculate(left, op, right):
        match op:
            case "+":
                return left + right
            case "-":
                return left - right
            case "*":
                return left * right
            case "/":
                return left / right
            case "%":
                return left % right
            case "^":
                return left ** right
            case "and":
                return left and right
            case "or":
                return left or right
            case "if":
                return left if right else None
            case "in":
                return left in right


class TernaryOperator(Expression):
    def __init__(self, op, first, second, third):
        self.op = op
        self.first = first
        self.second = second
        self.third = third

    def evaluate(self, ctx: Context):
        first = self.first.evaluate(ctx)
        second = self.second.evaluate(ctx)
        third = self.third.evaluate(ctx)
        match self.op:
            case "conditional":
                return first if second else third


class ComparisonOperator(BinaryOperator):
    def __init__(self, left, op, right):
        super().__init__(left, op, right)

    def evaluate(self, ctx: Context):
        left = self.left.evaluate(ctx)
        valid = True
        right = self.right.evaluate(ctx)

        # Chained comparison operators
        if type(self.left) == ComparisonOperator:
            left = self.left.right.evaluate(ctx)
            valid = self.left.evaluate(ctx)

        if not valid:
            return False
        match self.op:
            case "==":
                return left == right
            case "!=":
                return left != right
            case "<":
                return left < right
            case "<=":
                return left <= right
            case ">":
                return left > right
            case ">=":
                return left >= right


class FunctionCall(Expression):
    def __init__(self, function_expr, args):
        self.func_expr = function_expr
        self.args = args

    def evaluate(self, ctx: Context):
        func = self.func_expr.evaluate(ctx)
        if len(self.args) < func.arguments_needed():
            # If not enough arguments are given, return the same function
            # but with the curried arguments.
            curried = list(func.curried)
            curried.extend([expr.evaluate(ctx) for expr in self.args])
            return Function(func.parameters, func.block, curried)
        else:
            return func.execute(ctx, [expr.evaluate(ctx) for expr in self.args])


class VariableAccess(Expression):
    def __init__(self, var, post_condition=lambda x: True, error_message=None):
        self.var = var
        self.post_condition = post_condition
        self.error_message = error_message

    def evaluate(self, ctx: Context):
        result = ctx.variables()[self.var] if self.var in ctx.variables() else None
        if not self.post_condition(result):
            raise RuntimeError("The variable did not comply with the condition"
                               if self.error_message is None
                               else self.error_message)
        return result


class VariableChange(Expression):
    def __init__(self, var, op, expr=None):
        self.var = var
        self.op = op
        self.expr = expr

    def evaluate(self, ctx: Context):
        if self.var not in ctx.variables():
            ctx.variables()[self.var] = 0
        match self.op:
            case "del":
                return ctx.variables().pop(self.var) if self.var in ctx.variables() else None
            case "=":
                ctx.variables()[self.var] = self.expr.evaluate(ctx)
            case "+=":
                ctx.variables()[self.var] += self.expr.evaluate(ctx)
            case "-=":
                ctx.variables()[self.var] -= self.expr.evaluate(ctx)
            case "++":
                ctx.variables()[self.var] += 1
            case "--":
                ctx.variables()[self.var] -= 1
        return ctx.variables()[self.var]

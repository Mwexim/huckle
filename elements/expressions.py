from copy import copy
from enum import Enum
from utils.parser_utils import Context
from utils.primitives import Function, Matrix, Slice


class ChangeMode(Enum):
    ADD, ADD_ONE, DELETE, REMOVE, REMOVE_ONE, SET = "+=", "++", "del", "-=", "--", "="


class Expression:
    def evaluate(self, ctx: Context):
        raise NotImplementedError("This method should be implemented")

    def change(self, ctx: Context, mode: ChangeMode, value):
        raise RuntimeError("This expression cannot be changed")


class Primitive(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self, ctx: Context):
        return self.value


class NestedExpression(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def evaluate(self, ctx: Context):
        return self.expression.evaluate(ctx)

    def change(self, ctx: Context, mode: ChangeMode, value):
        self.expression.change(ctx, mode, value)


class MatrixExpression(Expression):
    def __init__(self, last_operation: 'MatrixOperation' = None):
        self.last_operation = last_operation

    def evaluate(self, ctx: Context):
        if self.last_operation is None:
            return Matrix()
        else:
            return self.last_operation.evaluate(ctx)


class UnitMatrixExpression(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def evaluate(self, ctx: Context):
        return Matrix(self.expression.evaluate(ctx))


class MatrixOperation(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self, ctx: Context):
        left: Matrix = self.left.evaluate(ctx)
        right = self.right.evaluate(ctx)
        match self.operator:
            case ",":
                # Add element to row or add column vector to matrix
                if isinstance(right, Matrix):
                    left.concat(right.rows(), dimension=1)
                else:
                    left.concat(right, dimension=1)
            case ";":
                # Add element to new row or add row vector to matrix
                if isinstance(right, Matrix):
                    left.concat(right.rows())
                else:
                    left.concat(right)
        return left


class UnaryOperator(Expression):
    def __init__(self, operator: str, expression: Expression):
        self.operator = operator
        self.expression = expression

    def evaluate(self, ctx: Context):
        expression = self.expression.evaluate(ctx)
        match self.operator:
            case "-":
                return -expression
            case "not":
                return not expression


class BinaryOperator(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression, commutative=True):
        self.left = left
        self.operator = operator
        self.right = right
        self.commutative = commutative

    def evaluate(self, ctx: Context):
        left = self.left.evaluate(ctx)
        right = self.right.evaluate(ctx)
        try:
            result = self.calculate(left, self.operator, right)
            return result
        except:
            # Sometimes, we only want to define operations on one type.
            # An example is the matrix multiplication with a scalar.
            if self.commutative:
                result = self.calculate(right, self.operator, left)
                return result

    @staticmethod
    def calculate(left, operator, right):
        match operator:
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
    def __init__(self, operator: str, first: Expression, second: Expression, third: Expression):
        self.operator = operator
        self.first = first
        self.second = second
        self.third = third

    def evaluate(self, ctx: Context):
        first = self.first.evaluate(ctx)
        second = self.second.evaluate(ctx)
        third = self.third.evaluate(ctx)
        match self.operator:
            case "conditional":
                return first if second else third
            case "slice":
                return Slice(first, second, third)


class ComparisonOperator(BinaryOperator):
    def __init__(self, left: Expression, operator: str, right: Expression):
        super().__init__(left, operator, right)

    def evaluate(self, ctx: Context):
        left = self.left.evaluate(ctx)
        valid = True
        right = self.right.evaluate(ctx)

        # Chained comparison operators
        if isinstance(self.left, ComparisonOperator):
            left = self.left.right.evaluate(ctx)
            valid = self.left.evaluate(ctx)

        if not valid:
            return False
        match self.operator:
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
    def __init__(self, expression: Expression, arguments: list[Expression]):
        self.expression = expression
        self.arguments = arguments

    def evaluate(self, ctx: Context):
        func = self.expression.evaluate(ctx)
        if len(self.arguments) < func.arguments_needed():
            # If not enough arguments are given, return the same function
            # but with the curried arguments.
            curried = list(func.curried)
            curried.extend([expr.evaluate(ctx) for expr in self.arguments])
            return Function(func.parameters, func.block, curried)
        else:
            return func.execute(ctx, [expr.evaluate(ctx) for expr in self.arguments])

    def change(self, ctx: Context, mode: ChangeMode, value):
        # TODO Add preconditions
        # Currently, only Matrices can have their values changed by calling them as a function
        changing = self.expression.evaluate(ctx)
        match mode:
            case ChangeMode.ADD:
                changing[[expr.evaluate(ctx) for expr in self.arguments]] += value
            case ChangeMode.ADD_ONE:
                changing[[expr.evaluate(ctx) for expr in self.arguments]] += 1
            case ChangeMode.DELETE:
                del changing[[expr.evaluate(ctx) for expr in self.arguments]]
            case ChangeMode.REMOVE:
                changing[[expr.evaluate(ctx) for expr in self.arguments]] -= value
            case ChangeMode.REMOVE_ONE:
                changing[[expr.evaluate(ctx) for expr in self.arguments]] -= 1
            case ChangeMode.SET:
                changing[[expr.evaluate(ctx) for expr in self.arguments]] = value
        return changing


class VariableAccess(Expression):
    def __init__(self, identifier: str, post_condition=lambda x: True, error_message=None):
        self.identifier = identifier
        self.post_condition = post_condition
        self.error_message = error_message

    def evaluate(self, ctx: Context):
        result = ctx.variables()[self.identifier] if self.identifier in ctx.variables() else None
        if not self.post_condition(result):
            raise RuntimeError("The variable did not comply with the condition"
                               if self.error_message is None
                               else self.error_message)
        return result

    def change(self, ctx: Context, mode: ChangeMode, value):
        match mode:
            case ChangeMode.ADD:
                ctx.variables()[self.identifier] += value
            case ChangeMode.ADD_ONE:
                ctx.variables()[self.identifier] += 1
            case ChangeMode.DELETE:
                return ctx.variables().pop(self.identifier) if self.identifier in ctx.variables() else None
            case ChangeMode.REMOVE:
                ctx.variables()[self.identifier] -= value
            case ChangeMode.REMOVE_ONE:
                ctx.variables()[self.identifier] -= 1
            case ChangeMode.SET:
                ctx.variables()[self.identifier] = value
        return ctx.variables()[self.identifier]


class VariableChange(Expression):
    def __init__(self, changing: Expression, operator: str, change_to: Expression = None):
        self.changing = changing
        self.operator = operator
        self.change_to = change_to

    def evaluate(self, ctx: Context):
        # if self.changing not in ctx.variables():
        #     ctx.variables()[self.changing] = 0
        return self.changing.change(ctx,
                                    ChangeMode(self.operator),
                                    copy(self.change_to.evaluate(ctx)) if self.change_to is not None else None)

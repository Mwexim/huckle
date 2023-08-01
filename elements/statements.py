from utils.parser_utils import Context


def run_statements(start, ctx, predicate=lambda x: x is not None, debug=False):
    """
    Runs all statements in a program. It starts by running the first statement, and then fetching
    the following statement by calling the walk method. This continues until there is no following
    statement to be found. The program has ended.
    :param start: the first statement
    :param ctx: the context
    :param predicate: the condition to keep running the next statement
    :param debug: whether to output debug messages
    :return: the last statement that was called
    """
    current = start
    if debug:
        print("DEBUG: Currently walking over", current)
    following = start.walk(ctx)
    while predicate(following):
        current = following
        if debug:
            print("DEBUG: Currently walking over", current)
        following = current.walk(ctx)
    else:
        return current


class Statement:
    def __init__(self, parent=None, next=None):
        self.parent = parent
        self.next = next

    def take_next(self, ctx: Context):
        if self.next is not None:
            return self.next
        elif self.parent is not None:
            return self.parent.take_next(ctx)
        else:
            return None

    def walk(self, ctx: Context):
        self.run(ctx)
        return self.take_next(ctx)

    def run(self, ctx: Context):
        raise NotImplementedError("This method should be implemented if the walk method is not")

    def clear(self, ctx: Context):
        pass

    def find_parent(self, cls):
        parent = self.parent
        while parent is not None and type(parent) != cls:
            parent = parent.parent
        return parent


class StatementWrapper(Statement):
    def __init__(self, expression, parent=None, next=None):
        super().__init__(parent, next)
        self.expression = expression

    def run(self, ctx: Context):
        self.expression.evaluate(ctx)


# The way this is implemented makes it a statement and not a block.
# It doesn't need the children functionality.
class ConditionalStatement(Statement):
    def __init__(self, if_expression, if_block, parent=None, next=None):
        super().__init__(parent, next)

        self.if_expression = if_expression
        self.if_block = if_block
        self.if_block.parent = self

        self.elif_expressions = []
        self.elif_blocks = []

        self.else_block = None

    def add_elif(self, expression, block):
        block.parent = self
        self.elif_expressions.append(expression)
        self.elif_blocks.append(block)
        block.parent = self

    def set_else(self, block):
        self.else_block = block
        self.else_block.parent = self

    def walk(self, ctx: Context):
        if self.if_expression.evaluate(ctx):
            return self.if_block
        for i in range(len(self.elif_expressions)):
            if self.elif_expressions[i].evaluate(ctx):
                return self.elif_blocks[i]
        if self.else_block is not None:
            return self.else_block
        return self.take_next(ctx)


class PassStatement(Statement):
    def __init__(self, parent=None, next=None):
        super().__init__(parent, next)

    def run(self, ctx: Context):
        pass


class ReturnStatement(Statement):
    def __init__(self, expression, parent=None, next=None):
        super().__init__(parent, next)
        self.expression = expression

    def walk(self, ctx: Context):
        return_block = self.find_parent(ReturnBlock)
        return_block.returned = self.expression.evaluate(ctx)
        return return_block


class ContinueStatement(Statement):
    def __init__(self, parent=None, next=None):
        super().__init__(parent, next)

    def walk(self, ctx: Context):
        block = self.find_parent(WhileBlock)
        # We need to manually take the next item, since the while-condition is checked in there.
        return block.take_next(ctx)


class Block(Statement):
    def __init__(self, parent=None, next=None):
        super().__init__(parent, next)
        self.children = []

    def set_children(self, children):
        self.children = children
        for i in range(len(children) - 1, -1, -1):
            self.children[i].parent = self
            self.children[i].next = self.children[i + 1] if i + 1 < len(children) else None

    def walk(self, ctx: Context):
        return self.children[0] if len(self.children) > 0 else self.take_next(ctx)


class ReturnBlock(Block):
    def __init__(self, parent=None, next=None):
        super().__init__(parent, next)
        self.returned = None

    def walk(self, ctx: Context):
        # The return block is a special block encapsulated by the function definition call.
        # We know the function definition call handles the returned value and clears the data,
        # so we won't be running any further statements.
        # This prevents multiple functions returning at once, but so be it.
        return self.children[0] if len(self.children) > 0 and self.returned is None else self.take_next(ctx)

    def clear(self, ctx: Context):
        # Needs to be called by the function definition call!
        self.returned = None


class WhileBlock(Block):
    def __init__(self, expression, parent=None, next=None):
        super().__init__(parent, next)
        self.expression = expression

    def take_next(self, ctx):
        if self.expression.evaluate(ctx):
            return self
        elif self.next is not None:
            return self.next
        elif self.parent is not None:
            return self.parent.take_next(ctx)
        else:
            return None

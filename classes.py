class Context:
    variable_states = list()

    def __init__(self):
        self.variable_states.append(dict())

    def branch(self, seek_return=False, state_type=""):
        pass
        # self.variable_states.append(dict(self.variables()))
        # if seek_return:
        #     self.return_states.append([len(self.variable_states) - 1, None])
        # if len(state_type) > 0:
        #     self.state_indices.append([state_type, len(self.variable_states) - 1])

    def pop(self, keep_shadowed_variables=False):
        pass
        # local_variables = self.variable_states.pop()
        # while len(self.return_states) > 0 and self.return_states[-1][0] > len(self.variable_states):
        #     self.return_states.pop()
        #
        # # After some branched contexts, like in an if-block, we want to keep
        # # variables that were defined outside the scope but used inside.
        # # TODO Refine the implementation, because it has limitations.
        # if keep_shadowed_variables:
        #     for key in self.variables():
        #         if key in local_variables:
        #             self.variables()[key] = local_variables[key]

    def variables(self):
        return self.variable_states[-1]


class Function:
    def __init__(self, parameters, block, curried=None):
        self.parameters = parameters
        self.block = block
        self.curried = [] if curried is None else curried

    def execute(self, ctx: Context, args):
        if len(self.parameters) < len(self.curried) + len(args):
            raise RuntimeError(f"Too many arguments: expected {len(self.parameters)} arguments, but found {len(self.curried) + len(args)}")

        for i, parameter in enumerate(self.parameters):
            ctx.variables()[parameter] = self.curried[i] if i < len(self.curried) else args[i - len(self.curried)]

        from elements.statements import run_statements
        run_statements(self.block, ctx, predicate=lambda x: x is not None and self.block.returned is None)
        returned = self.block.returned
        self.block.clear()

        return returned

    def arguments_needed(self):
        return len(self.parameters) - len(self.curried)

    def __str__(self):
        return f'fn({", ".join(self.parameters)})'

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


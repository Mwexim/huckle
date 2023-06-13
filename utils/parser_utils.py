class Context:
    variable_states = []

    def __init__(self):
        self.variable_states.append(dict())
        
    def variables(self):
        return self.variable_states[-1]
    
    # def branch(self):
    #     self.variable_states.append(dict(self.variables()))
    #     from main import DEBUG
    #     if DEBUG:
    #         print(f"DEBUG: Branching out, currently {len(self.variable_states)} states present.")
    #         print(f"DEBUG: Variables dictionary: {self.variables()}")
    #
    # def merge(self, keep_shadowed_references=True):
    #     popped = self.variable_states.pop()
    #     from main import DEBUG
    #     if DEBUG:
    #         print(f"DEBUG: Variables before merging: {self.variables()}")
    #         print(f"DEBUG: Keep shadowed references: {keep_shadowed_references}")
    #     if keep_shadowed_references:
    #         for (key, value) in popped.items():
    #             self.variables()[key] = value
    #     if DEBUG:
    #         print(f"DEBUG: Merging, now only {len(self.variable_states)} states remaining.")
    #         print(f"DEBUG: Variables after merging: {self.variables()}")



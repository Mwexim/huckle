from elements.statements import run_statements
from lexer import initiate_lexer
from parser import initiate_parser, initiate_context
from utils.primitives import Complex

# TODO Add tuples (up for debate)
# TODO Element-wise division, multiplication
# TODO Matrix row/column operators like ';=' or ',=' (up for debate)
# TODO Complex numbers and their functions
# TODO Add matrix de-referencing like '[P, J] = eig(A)'
# TODO Fix ALL shift/reduce conflicts (possibly by recreating the parser itself from scratch)
# TODO Create a local variable system
# TODO Add vector type and better conversion between vectors and matrices
# TODO Optimize parser and use more specific grammar rules that convert to expressions
# TODO Listable parent class for matrices, vectors, slices and tuples
# TODO Rework the expandable parameter system to be unified for all listable types
# TODO Fix issue where comments/newlines on top of the file are not allowed
# TODO Decorator for parser functions
# TODO Rewrite the parser rules by hand

# File to be parsed
source = open("resources/test.hk", "r").read() + "\n"

# Build the parser and lexer
lexer, tokens = initiate_lexer(source)
parser = initiate_parser(tokens)

program = parser.parse(source, lexer=lexer, debug=False)
run_statements(program, initiate_context(), debug=False)


# Explanation mode
# for block in source.split("# "):
#     lines = block.split("\n")
#     if len(lines) >= 1:
#         print()
#         print(lines[0])
#         first_printed = False
#         for line in lines[1:]:
#             if first_printed:
#                 print()
#             first_printed = True
#             print(line)
#             if line.startswith(">> "):
#                 execute_program(line[len(">> "):], lexer, parser, expression_only=True)
#             else:
#                 execute_program(line, lexer, parser)

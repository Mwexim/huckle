from elements.statements import run_statements
from lexer import initiate_lexer
from parser import initiate_parser, initiate_context

# TODO Add tuples (up for debate)
# TODO Element-wise division, multiplication
# TODO Matrix row/column operators like ';=' or ',=' (up for debate)
# TODO Add matrix dereferencing like '[P, J] = eig(A)'
# TODO Transpose operator (up for debate, no new conflicts)
# TODO Fix ALL shift/reduce conflicts
# TODO Create a local variable system
# TODO Add vector type and better conversion between vectors and matrices
# TODO Optimize parser and use more specific grammer rules that convert to expressions
# TODO Listable parent class for matrices, vectors, slices and tuples

# File to be parsed
source = open("resources/test.hk", "r").read() + "\n"

# Build the parser

lexer, tokens = initiate_lexer(source)
parser = initiate_parser(tokens)

# Testing zone

# lexer.input(source)
# while True:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)

# while True:
#     s = input('> ')
#     result = unpack(parser.parse(s))
#     print(result)

program = parser.parse(source, lexer=lexer, debug=False)
run_statements(program, initiate_context(), debug=False)

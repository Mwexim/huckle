from elements.statements import run_statements
from lexer import initiate_lexer
from parser import initiate_parser, initiate_context

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

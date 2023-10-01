import cmath
import math
import operator

from ply import yacc

from utils.builtins import *
from utils.primitives import *
from elements.expressions import *
from elements.statements import *


def initiate_parser(tokens):
    # Still has conflicts...
    precedence = [
        ("left", "SEMICOLON"),
        ("left", "COMMA"),
        # ("left", "COLON"),
        ("right", "ASSIGN", "PLUSASSIGN", "PLUSONE", "MINUSASSIGN", "MINUSONE"),
        # Here to handle infix operator priority, but not an ideal solution?
        # The line below with the BININFIX precedence override does not seem to work...
        ("left", "ID"),
        # ("left", "BININFIX"),
        ("right", "IF", "ELSE"),
        ("left", "AND"),
        ("left", "OR"),
        ("right", "NOT"),
        ("nonassoc", "IN"),
        ("left", "EQ", "NEQ", "GT", "GTE", "LT", "LTE"),
        ("left", "PLUS", "MIN"),
        ("left", "TIMES", "ELTIMES", "DIV", "MOD"),
        ("left", "POW", "ELPOW"),
        ("right", "UMINUS", "QUOTE"),
        # Needed for expression calling?
        ("nonassoc", "LPAREN"),
        ("nonassoc", "LBRACKET")
    ]

    # *************
    # PROGRAM RULES
    # *************
    def p_program(p):
        # TODO Make it so that a file can start with a newline/comment
        """
        block : statement
              | block NL
              | block NL statement
        """
        if len(p) == 2:
            p[0] = Block()
            p[0].set_children([p[1]])
        elif len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = p[1]
            children = list(p[0].children)
            children.append(p[3])
            p[0].set_children(children)

    # ***********
    # BLOCK RULES
    # ***********
    def p_while_block(p):
        """
        statement : WHILE expression COLON IND block DED
        """
        p[0] = WhileBlock(p[2])
        p[0].set_children([p[5]])

    def p_for_block(p):
        """
        statement : FOR ID IN expression COLON IND block DED
        """
        p[0] = ForBlock(p[2], p[4])
        p[0].set_children([p[7]])

    # ***************
    # STATEMENT RULES
    # ***************
    def p_simple_statements(p):
        """
        statement : CONTINUE
                  | PASS
        """
        match p[1]:
            case "continue":
                p[0] = ContinueStatement()
            case "pass":
                p[0] = PassStatement()

    def p_return_statement(p):
        """
        statement : RETURN expression
        """
        p[0] = ReturnStatement(p[2])

    def p_conditional_statement(p):
        # If you're using custom terminals and after DED there can immediately follow another terminal instead
        # of NL, you must add an extra rule!
        """
        conditional : IF expression COLON IND block DED
                    | conditional ELIF expression COLON IND block DED
        statement : conditional
                  | conditional ELSE COLON IND block DED
        """
        if len(p) == 7 and p[1] == "if":
            p[0] = ConditionalStatement(p[2], p[5])
        elif len(p) == 7 and p[2] == "else":
            conditional = p[1]
            conditional.set_else(p[5])
            p[0] = conditional
        elif len(p) == 8:
            conditional = p[1]
            conditional.add_elif(p[3], p[6])
            p[0] = conditional
        else:
            p[0] = p[1]

    def p_convert_expressions(p):
        """
        statement : expression
        """
        p[0] = StatementWrapper(p[1])

    # ****************
    # EXPRESSION RULES
    # ****************
    def p_expression_hierarchy(p):
        """
        parameter_expression : expression
                             | slice
        """
        p[0] = p[1]

    def p_function_call(p):
        """
        expression : expression LPAREN parameters RPAREN
                   | expression DOT LPAREN parameters RPAREN
                   | expression LPAREN RPAREN
        parameters : parameter_expression
                   | parameters COMMA parameter_expression
        """
        # These slice hacks are necessary because the YaccProduction class has other behavior for negative indices
        # TODO Remove the slice hacks
        if len(p) >= 4 and p[:][-1] == ")":
            args = []
            if p[3] != ")":
                args.extend(p[:][-2])
            p[0] = FunctionCall(p[1], args, spread=p[2] == ".")
        elif len(p) == 4 and p[2] == ",":
            args = list(p[1])
            args.append(p[3])
            p[0] = args
        else:
            p[0] = [p[1]]

    def p_infix_operator(p):
        """
        expression : expression ID expression
                   | expression ID DOT expression
        """
        p[0] = FunctionCall(VariableAccess(p[2], lambda x: x.infix, "This function is not an infix function"),
                            [p[1], p[:][-1]],
                            spread=len(p) == 5)

    def p_list_access(p):
        """
        expression : expression LBRACKET parameters RBRACKET
                   | expression LBRACKET RBRACKET
        """
        if len(p) >= 4 and p[2] == "[":
            args = []
            if p[3] != "]":
                args.extend(p[3])
            p[0] = ListAccess(p[1], args)

    def p_function_definition(p):
        # The first argument needs to be defined separately, otherwise it clashes with another rule:
        # - expression : ID
        """
        expression : INFIX function_definition
                   | function_definition
        function_definition : FUN parameter_declaration COLON IND block DED
                            | FUN COLON IND block DED
                            | FUN parameter_declaration COLON expression
                            | FUN COLON expression
        parameter_declaration : ID
                              | parameter_declaration COMMA ID
        """
        if len(p) == 3 and p[1] == "infix":
            function = p[2]
            function.infix = True
            p[0] = Primitive(function)
        elif len(p) == 2:
            if isinstance(p[1], str):
                p[0] = [p[1]]
            else:
                p[0] = Primitive(p[1])
        elif p[1] == "fn":
            return_block = ReturnBlock()
            if len(p) == 7:
                # Function block with arguments provided
                return_block.set_children([p[5]])
            elif len(p) == 5:
                # Inline function with arguments provided
                return_block.set_children([ReturnStatement(p[4])])
            elif len(p) == 6:
                # Function block with no arguments
                return_block.set_children([p[4]])
                p[0] = Function([], return_block)
                return
            else:
                # Inline function with no arguments
                assert len(p) == 4
                return_block.set_children([ReturnStatement(p[3])])
                p[0] = Function([], return_block)
                return

            p[0] = Function(p[2], return_block)
        elif p[2] == ",":
            parameter_declaration = list(p[1])
            parameter_declaration.append(p[3])
            p[0] = parameter_declaration

    def p_matrix(p):
        """
        expression : LBRACKET matrix RBRACKET
                   | LBRACKET RBRACKET
        matrix : parameter_expression
               | matrix COMMA matrix
               | matrix SEMICOLON matrix
        """
        if len(p) == 4 and p[1] == "[" and p[3] == "]":
            p[0] = MatrixExpression(p[2])
        elif len(p) == 3 and p[1] == "[" and p[2] == "]":
            p[0] = MatrixExpression()
        elif len(p) == 2:
            p[0] = UnitMatrixExpression(p[1])
        else:
            p[0] = MatrixOperation(p[1], p[2], p[3])

    def p_change_variable(p):
        """
        expression : expression ASSIGN expression
                   | expression PLUSASSIGN expression
                   | expression PLUSONE
                   | expression MINUSASSIGN expression
                   | expression MINUSONE
                   | DEL expression
        """
        if p[1] == "del":
            p[0] = VariableChange(p[2], p[1])
        elif len(p) == 3:
            p[0] = VariableChange(p[1], p[2])
        else:
            p[0] = VariableChange(p[1], p[2], p[3])

    def p_variable_access(p):
        """
        expression : ID
        """
        p[0] = VariableAccess(p[1])

    def p_unary_operators(p):
        """
        expression : MIN expression %prec UMINUS
                   | NOT expression
                   | expression QUOTE
        """
        if p[2] == "'":
            p[0] = UnaryOperator(p[2], p[1])
        else:
            p[0] = UnaryOperator(p[1], p[2])

    def p_binary_operators(p):
        """
        expression : expression PLUS expression
                   | expression MIN expression
                   | expression TIMES expression
                   | expression ELTIMES expression
                   | expression DIV expression
                   | expression MOD expression
                   | expression POW expression
                   | expression ELPOW expression
                   | expression AND expression
                   | expression OR expression
                   | expression IF expression
                   | expression IN expression
        """
        p[0] = BinaryOperator(p[1], p[2], p[3], p[2] not in ("%", "if", "in"))

    def p_id_and_coefficient(p):
        """
        expression : ID_AND_COEFF
        """
        p[0] = BinaryOperator(Primitive(p[1][0]), "*", VariableAccess(p[1][1]))

    def p_comparison(p):
        """
        expression : expression EQ expression
                   | expression NEQ expression
                   | expression LT expression
                   | expression LTE expression
                   | expression GT expression
                   | expression GTE expression
        """
        p[0] = ComparisonOperator(p[1], p[2], p[3])

    def p_ternary_operators(p):
        """
        expression : expression IF expression ELSE expression
        """
        p[0] = TernaryOperator("conditional", p[1], p[3], p[5])

    def p_slice_operator(p):
        """
        slice : expression COLON expression COLON expression
              | COLON expression COLON expression
              | expression COLON COLON expression
              | expression COLON expression
              | COLON COLON expression
              | COLON expression
              | expression COLON
              | COLON
        """
        start = Primitive(None)
        end = Primitive(None)
        step = Primitive(None)
        separators = 0
        for match in p[1:]:
            if match == ":":
                separators += 1
            elif separators == 0:
                start = match
            elif separators == 1:
                end = match
            elif separators == 2:
                step = match
        p[0] = TernaryOperator("slice", start, end, step)

    def p_parantheses(p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = NestedExpression(p[2])

    def p_primitives(p):
        """
        expression : NUMBER
                   | COMPLEX
                   | BOOLEAN
                   | STRING
                   | NONE
        """
        p[0] = Primitive(p[1])

    # ***********
    # ERROR RULES
    # ***********
    def p_error(p):
        print("Syntax error in input:", p)

    return yacc.yacc(outputdir="output")


def initiate_context():
    ctx = Context()

    ctx.variable_states[-1] = {
        # Python functions, later on these will be built-in
        "len": PythonFunction(len),
        "slice": PythonFunction(Slice),
        "str": PythonFunction(str),

        # Built-in functions
        "print": ContextFunction(pretty_print),

        # Logic functions
        "eq": PythonFunction(operator.eq, infix=True),

        # Matrix functions
        "cross": PythonFunction(cross, infix=True),
        "det": PythonFunction(determinant),
        "diagonal": PythonFunction(diagonal),
        "dot": PythonFunction(dot, infix=True),
        "eye": PythonFunction(eye),
        "inv": PythonFunction(inverse),
        "max": PythonFunction(maximum),
        "min": PythonFunction(minimum),
        "norm": PythonFunction(norm),
        "ones": PythonFunction(ones),
        "rank": PythonFunction(rank),
        "reshape": PythonFunction(reshape, infix=True),
        "trace": PythonFunction(trace),
        "transpose": PythonFunction(transpose),
        "zeros": PythonFunction(zeros),

        # Imaginary number functions
        "conj": PythonFunction(Complex.conjugate),
        "imag": PythonFunction(imag),
        "phase": PythonFunction(cmath.phase),
        "polar": PythonFunction(polar),
        "real": PythonFunction(real),

        # Basic math functions
        "abs": PythonFunction(abs),
        "acos": PythonFunction(math.acos),
        "acosh": PythonFunction(math.acosh),
        "asin": PythonFunction(math.asin),
        "asinh": PythonFunction(math.asinh),
        "atan": PythonFunction(math.atan),
        "atanh": PythonFunction(math.atanh),
        "cos": PythonFunction(math.cos),
        "cosh": PythonFunction(math.cosh),
        "exp": PythonFunction(math.exp),
        "log": PythonFunction(math.log),
        "sin": PythonFunction(math.sin),
        "sinh": PythonFunction(math.sinh),
        "sqrt": PythonFunction(sqrt),
        "tan": PythonFunction(math.tan),
        "tanh": PythonFunction(math.tanh),

        # Built-in variables
        "e": math.e,
        "i": Complex(0, 1),
        "pi": math.pi,
        "pretty_print": True
    }

    return ctx

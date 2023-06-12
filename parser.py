from ply import yacc
from classes import PythonFunction
from elements.expressions import *
from elements.statements import *


def initiate_parser(tokens):
    # Still has 19 conflicts...
    precedence = [
        ("right", "ASSIGN", "PLUSASSIGN", "PLUSONE", "MINUSASSIGN", "MINUSONE"),
        ("right", "IF", "ELSE"),
        ("left", "AND"),
        ("left", "OR"),
        ("right", "NOT"),
        ("nonassoc", "IN"),
        ("left", "EQ", "NEQ", "GT", "GTE", "LT", "LTE"),
        ("left", "PLUS", "MIN"),
        ("left", "TIMES", "DIV", "MOD"),
        ("left", "POW"),
        ("right", "UMINUS"),
        # Needed for expression calling?
        ("nonassoc", "LPAREN")
    ]

    # TODO Work with statements and expression to distinguish the two better
    def p_program(p):
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

    def p_while_block(p):
        """
        statement : WHILE expression COLON IND block DED
        """
        p[0] = WhileBlock(p[2])
        p[0].set_children([p[5]])

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

    def p_convert_expressions(p):
        """
        statement : expression
        """
        p[0] = StatementWrapper(p[1])

    def p_conditional_block(p):
        # If you're using custom terminals and after DED there can immediately follow another terminal instead
        # of NL, you must add an extra rule!
        """
        conditional : IF expression COLON IND block DED
                    | conditional ELIF expression COLON IND block DED
                    | conditional NL
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

    def p_function_call(p):
        """
        expression : expression LPAREN parameters RPAREN
                   | expression LPAREN RPAREN
        parameters : expression
                   | parameters COMMA expression
        """
        if len(p) >= 4 and p[2] == "(":
            args = []
            if p[3] != ")":
                args.extend(p[3])
            p[0] = FunctionCall(p[1], args)
        elif len(p) >= 4 and p[2] == ",":
            args = list(p[1])
            args.append(p[3])
            p[0] = args
        else:
            p[0] = [p[1]]

    def p_function_definition(p):
        # The first argument needs to be defined separately, otherwise it clashes with another rule:
        # - expression : ID
        """
        expression : FUN LPAREN declaration RPAREN COLON IND block DED
                   | FUN LPAREN ID RPAREN COLON IND block DED
                   | FUN LPAREN RPAREN COLON IND block DED
        declaration : ID COMMA ID
                    | declaration COMMA ID
        """
        if p[2] == "(" and p[4] == ")":
            if isinstance(p[3], str):
                # Otherwise one multiple character ID will be interpreted as a list of arguments!
                p[3] = [p[3]]
            return_block = ReturnBlock()
            return_block.set_children([p[7]])
            p[0] = Primitive(Function(list(p[3]), return_block))
        elif p[2] == "(" and p[3] == ")":
            return_block = ReturnBlock()
            return_block.set_children([p[6]])
            p[0] = Primitive(Function([], return_block))
        elif p[2] == "," and type(p[1]) != list:
            p[0] = [p[1], p[3]]
        elif p[2] == ",":
            declaration = list(p[1])
            declaration.append(p[3])
            p[0] = declaration

    def p_return_statement(p):
        """
        statement : RETURN expression
        """
        p[0] = ReturnStatement(p[2])

    def p_change_variable(p):
        """
        expression : ID ASSIGN expression
                   | ID PLUSASSIGN expression
                   | ID PLUSONE
                   | ID MINUSASSIGN expression
                   | ID MINUSONE
                   | DEL ID
        """
        p[0] = VariableChange(p[2], p[1]) if p[1] == "del" else VariableChange(p[1], p[2], p[3])

    def p_variable_access(p):
        """
        expression : ID
        """
        p[0] = VariableAccess(p[1])

    def p_unary_operators(p):
        """
        expression : MIN expression %prec UMINUS
        expression : NOT expression
        """
        p[0] = UnaryOperator(p[1], p[2])

    def p_binary_operators(p):
        """
        expression : expression PLUS expression
                   | expression MIN expression
                   | expression TIMES expression
                   | expression DIV expression
                   | expression MOD expression
                   | expression POW expression
                   | expression AND expression
                   | expression OR expression
                   | expression IF expression
                   | expression IN expression
        """
        p[0] = BinaryOperator(p[1], p[2], p[3])

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

    def p_primitives(p):
        """
        expression : NUMBER
                   | BOOLEAN
                   | STRING
                   | NONE
        """
        p[0] = Primitive(p[1])

    def p_parantheses(p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = NestedExpression(p[2])

    # Error rule for syntax errors
    def p_error(p):
        print("Syntax error in input:", p)

    return yacc.yacc(outputdir="output")


def initiate_context():
    ctx = Context()

    # Default functions
    ctx.variables()["max"] = PythonFunction(max)
    ctx.variables()["min"] = PythonFunction(min)
    ctx.variables()["print"] = PythonFunction(print)
    ctx.variables()["str"] = PythonFunction(str)

    return ctx
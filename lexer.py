from collections import deque
from ply import lex
from ply.lex import Lexer, LexToken


class IndentationToken(LexToken):
    def __init__(self, type):
        self.type = type
        self.value = None
        self.lineno = None
        self.lexpos = None
        self.lexer = None

    def complete(self, lexer):
        self.lineno = lexer.lineno
        self.lexpos = lexer.lexpos
        self.lexer = lexer
        return self


indent = IndentationToken("IND")
dedent = IndentationToken("DED")
newline = IndentationToken("NL")


class IndentLexer:
    """
    This wrapper class makes sure that indents are handled correctly, as the PLY lexing
    module is not powerful enough to add Python-like indentation rules.
    """
    def __init__(self, lexer: Lexer):
        """
        :param lexer: the lexer being wrapped
        """
        super().__init__()
        self.lexer = lexer
        self.indent_stack = [0]
        self.token_queue = deque()
        # This is just in case the ply-generated lexer cannot be called again
        # after it returns None.
        self.eof_reached = False

    def input(self, source: str):
        self.lexer.input(source)

    def token(self):
        """
        :return: the next token, or ``None`` if the end of input is reached
        """
        # Do we have any queued tokens?
        if self.token_queue:
            return self.token_queue.popleft()
        # Are we at the end of the file?
        if self.eof_reached:
            return None
        # Fetch the token
        t = self.lexer.token()
        if t is None:
            # At end of input, we might need to send some dedents
            self.eof_reached = True
            if len(self.indent_stack) > 1:
                t = dedent
                for i in range(len(self.indent_stack) - 1):
                    self.token_queue.append(dedent.complete(self.lexer))
                self.indent_stack = [0]
        elif t.type == "NL":
            # The NL token includes the amount of leading whitespace.
            # Fabricate indent or dedents as/if necessary and queue them.
            if t.value > self.indent_stack[-1]:
                self.indent_stack.append(t.value)
                self.token_queue.append(indent.complete(self.lexer))
                return self.token_queue.popleft()
            else:
                while t.value < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.token_queue.append(dedent.complete(self.lexer))
                if t.value != self.indent_stack[-1]:
                    # TODO Create a class for this
                    raise Exception("Indentation error")
                # Each statement must end with a newline, or multiple ones. Adding this ensures
                # that the user does not need an empty line after a dedent.
                self.token_queue.append(newline.complete(self.lexer))
                return self.token_queue.popleft()
        else:
            return t


def initiate_lexer(to_parse):
    # List of token names.
    keywords = {
        "if": "IF",
        "elif": "ELIF",
        "else": "ELSE",
        "while": "WHILE",
        "continue": "CONTINUE",
        "pass": "PASS",
        "del": "DEL",
        "in": "IN",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "fn": "FUN",
        "return": "RETURN",
        "infix": "INFIX",
        "=": "ASSIGN",
        "+=": "PLUSASSIGN",
        "++": "PLUSONE",
        "-=": "MINUSASSIGN",
        "--": "MINUSONE",
        "+": "PLUS",
        "-": "MIN",
        "*": "TIMES",
        "/": "DIV",
        "%": "MOD",
        "^": "POW",
        "==": "EQ",
        "!=": "NEQ",
        "<": "LT",
        "<=": "LTE",
        ">": "GT",
        ">=": "GTE",
        "(": "LPAREN",
        ")": "RPAREN",
        "[": "LBRACKET",
        "]": "RBRACKET",
        ",": "COMMA",
        ";": "SEMICOLON",
        ":": "COLON"
    }
    tokens = ["BOOLEAN", "STRING", "NUMBER", "NONE", "ID", "NL", "IND", "DED"] + list(keywords.values())

    # Tokenizers for the other tokens
    def t_NONE(t):
        r"None"
        t.value = None
        return t

    def t_BOOLEAN(t):
        r"(True|False)"
        t.value = True if t.value == "True" else False
        return t

    def t_STRING(t):
        r"\"[^\"]*\""
        t.value = t.value[1:-1]
        return t

    def t_NUMBER(t):
        r"\d+(\.\d*)?"
        if "." in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_ID(t):
        r"[a-zA-Z_][a-zA-Z_0-9]*\'?"
        # Check for reserved keywords
        t.type = keywords.get(t.value, "ID")
        return t

    def t_comment(t):
        r"\#[^\n]*"

    def t_NL(t):
        # Takes comments ('#') into account!
        r'\n(?:\t*(?:[#].*)?\n)*\t*'
        t.value = len(t.value) - 1 - t.value.rfind('\n')
        return t

    t_ignore = " \t"

    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Tokenizers for the operators
    for key, value in keywords.items():
        if not key.isalpha():
            locals()["t_" + value] = "".join(["\\" + c for c in key])

    # Build the lexer
    lexer = IndentLexer(lex.lex())
    return lexer, tokens

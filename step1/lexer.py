import argparse
import pathlib
import sys
from flask import jsonify
import ply.lex as lex

def breakToken(tok):
    array = tok.replace("LexToken(", "")
    array = array[:-1].split(",")
    id = array[0].replace("'", "")
    if (id == "COMMA"):
        value = ","
        line = array[3]
        collumn = array[4]
    else:
        value = array[1].replace("'", "")
        line = int(array[2])
        collumn = int(array[3])
    return {
        "id": id,
        "value": value,
        "line": line,
        "collumn": collumn
    }

class CompilerLexer:
    def __init__(self):
        self.filename = ""
        self.last_token = None

    def print_error(self, msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y), file=sys.stdout)

    def scan(self, data):
        dataMod = data[2:-1]
        self.lexer = lex.lex(object=self)
        self.lexer.input(dataMod)
        output = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            res = breakToken(str(tok))
            output.append(res)
        return jsonify(output)

    def reset_lineno(self):
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """Find the column of the token in its line."""
        last_cr = self.lexer.lexdata.rfind("\n", 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.print_error(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    # Reserved keywords
    keywords = (
        "ASSERT",
        "BREAK",
        "CHAR",
        "ELSE",
        "FLOAT",
        "FOR",
        "IF",
        "INT",
        "PRINT",
        "READ",
        "RETURN",
        "VOID",
        "WHILE",
    )

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    #
    # All the tokens recognized by the lexer
    #
    tokens = keywords + (
        # Identifiers
        "ID",
        "OR",
        "AND",
        "LBRACKET",
        "RBRACKET",
        "PLUSEQUAL",
        "MINUSEQUAL",
        "TIMESEQUAL",
        "MODEQUAL",
        "EQUALS",
        "DIVEQUAL",
        "LBRACE",
        "RBRACE",
        "LPAREN",
        "RPAREN",
        "COMMA",
        "CHAR_CONST",
        "STRING_LITERAL",
        "NOT",
        "SEMI",
        "LE",
        "PLUSPLUS",
        "TIMES",
        "MOD",
        "LT",
        "GE",
        "GT",
        "NE",
        "EQ",
        "PLUS",
        "MINUSMINUS",
        "MINUS",
        "DIVIDE",
        # constants
        "INT_CONST",
        "FLOAT_CONST",
    )

    #
    # Rules
    #
    t_ignore = " \t"

    # Newlines
    def t_NEWLINE(self, t):
        # include a regex here for newline
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_ONE_LINE_STAR_COMMENT(self, t):
        r'\/\*(.)*\*\/'
        t.lexer.lineno += t.value.count("\n")

    def t_COMMENT(self, t):
        # include a regex here for comment
        r'\/\*(.|\n)*\*\/'
        t.lexer.lineno += t.value.count("\n")

    def t_UNTERMINATED_COMMENT(self, t):
        r'\/\*(.|\n)*'
        msg = "Unterminated comment"
        self._error(msg, t)

    def t_LINE_COMMENT(self, t):
        r'\/\/.*'
        t.lexer.lineno += t.value.count("\n")

    def t_ID(self, t):
        # include a regex here for ID
        r'[_a-zA-Z][_a-zA-Z0-9]*'
        t.type = self.keyword_map.get(t.value, "ID")
        return t

    def t_OR(self, t):
        r'\|\|'
        t.type = self.keyword_map.get(t.value, "OR")
        return t

    def t_AND(self, t):
        r'&&'
        t.type = self.keyword_map.get(t.value, "AND")
        return t

    def t_FLOAT_CONST(self, t):
        r'[0-9]*\.[0-9]+'
        t.type = self.keyword_map.get(t.value, "FLOAT_CONST")
        return t

    def t_INT_CONST(self, t):
        r'[0-9]+'
        t.type = self.keyword_map.get(t.value, "INT_CONST")
        return t

    def t_LBRACKET(self, t):
        r'\['
        t.type = self.keyword_map.get(t.value, "LBRACKET")
        return t

    def t_RBRACKET(self, t):
        r'\]'
        t.type = self.keyword_map.get(t.value, "RBRACKET")
        return t

    def t_LBRACE(self, t):
        r'\{'
        t.type = self.keyword_map.get(t.value, "LBRACE")
        return t

    def t_RBRACE(self, t):
        r'\}'
        t.type = self.keyword_map.get(t.value, "RBRACE")
        return t

    def t_LPAREN(self, t):
        r'\('
        t.type = self.keyword_map.get(t.value, "LPAREN")
        return t

    def t_RPAREN(self, t):
        r'\)'
        t.type = self.keyword_map.get(t.value, "RPAREN")
        return t

    def t_COMMA(self, t):
        r','
        t.type = self.keyword_map.get(t.value, "COMMA")
        return t

    def t_CHAR_CONST(self, t):
        r'\'.\''
        t.type = self.keyword_map.get(t.value, "CHAR_CONST")
        return t

    def t_STRING_LITERAL(self, t):
        r'\"(.*?)\"'
        t.value = t.value.strip('"')
        t.type = self.keyword_map.get(t.value, "STRING_LITERAL")
        return t

    def t_SEMI(self, t):
        r';'
        t.type = self.keyword_map.get(t.value, "SEMI")
        return t

    def t_PLUSEQUAL(self, t):
        r'\+='
        t.type = self.keyword_map.get(t.value, "PLUSEQUAL")
        return t

    def t_MINUSEQUAL(self, t):
        r'-='
        t.type = self.keyword_map.get(t.value, "MINUSEQUAL")
        return t

    def t_TIMESEQUAL(self, t):
        r'\*='
        t.type = self.keyword_map.get(t.value, "TIMESEQUAL")
        return t

    def t_MODEQUAL(self, t):
        r'%='
        t.type = self.keyword_map.get(t.value, "MODEQUAL")
        return t

    def t_NE(self, t):
        r'!='
        t.type = self.keyword_map.get(t.value, "NE")
        return t

    def t_NOT(self, t):
        r'!'
        t.type = self.keyword_map.get(t.value, "NOT")
        return t

    def t_EQ(self, t):
        r'=='
        t.type = self.keyword_map.get(t.value, "EQ")
        return t

    def t_EQUALS(self, t):
        r'='
        t.type = self.keyword_map.get(t.value, "EQUALS")
        return t

    def t_DIVEQUAL(self, t):
        r'/='
        t.type = self.keyword_map.get(t.value, "DIVEQUAL")
        return t

    def t_PLUSPLUS(self, t):
        r'\+\+'
        t.type = self.keyword_map.get(t.value, "PLUSPLUS")
        return t

    def t_PLUS(self, t):
        r'\+'
        t.type = self.keyword_map.get(t.value, "PLUS")
        return t

    def t_MINUSMINUS(self, t):
        r'--'
        t.type = self.keyword_map.get(t.value, "MINUSMINUS")
        return t

    def t_MINUS(self, t):
        r'-'
        t.type = self.keyword_map.get(t.value, "MINUS")
        return t

    def t_TIMES(self, t):
        r'\*'
        t.type = self.keyword_map.get(t.value, "TIMES")
        return t

    def t_DIVIDE(self, t):
        r'/'
        t.type = self.keyword_map.get(t.value, "DIVIDE")
        return t

    def t_LE(self, t):
        r'<='
        t.type = self.keyword_map.get(t.value, "LE")
        return t

    def t_MOD(self, t):
        r'%'
        t.type = self.keyword_map.get(t.value, "MOD")
        return t

    def t_LT(self, t):
        r'<'
        t.type = self.keyword_map.get(t.value, "LT")
        return t

    def t_GE(self, t):
        r'>='
        t.type = self.keyword_map.get(t.value, "GE")
        return t

    def t_GT(self, t):
        r'>'
        t.type = self.keyword_map.get(t.value, "GT")
        return t

    def t_error(self, t):
        msg = "Illegal character %s" % repr(t.value[0])
        self._error(msg, t)
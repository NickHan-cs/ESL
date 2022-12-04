reserver_map = {
    "int": "INTTK", "float": "FLTTK", "array": "ARRTK",
    "void": "VOIDTK",  "main": "MAINTK", "if": "IFTK",
    "else": "ELSETK", "while": "WHILETK", "return": "RETURNTK",
    "in": "INTK", "out": "OUTTK", "break": "BRKTK",
}


class Token(object):

    def __init__(self, line, token_sym, token_str):
        self.line = line
        self.token_sym = token_sym
        self.token_str = token_str


def get_reserver_num(token_str):
    if token_str in reserver_map:
        return reserver_map[token_str]
    return "IDENFR"

def get_new_token(input_file):
    ch, line = input_file.getch()
    while ch == ' ' or ch == '\n' or ch == '\t':
        ch, line = input_file.getch()
    if ch is None:
        return None
    token_str = ""
    token_sym = -1
    if ch.isalpha() or ch == "_":
        while ch.isalpha() or ch == "_" or ch.isdigit():
            token_str += ch
            ch = input_file.getch()[0]
        input_file.retract()
        token_sym = get_reserver_num(token_str)
    elif ch.isdigit():
        while ch.isdigit():
            token_str += ch
            ch = input_file.getch()[0]
        token_sym = "INTCON"
        if ch == ".":
            token_str += ch
            ch = input_file.getch()[0]
            while ch.isdigit():
                token_str += ch
                ch = input_file.getch()[0]
            token_sym = "FLTCON"
        input_file.retract()
    elif ch == "+":
        token_str += ch
        token_sym = "PLUS"
    elif ch == "-":
        token_str += ch
        token_sym = "MINU"
    elif ch == "*":
        token_str += ch
        token_sym = "MULT"
    elif ch == "/":
        token_str += ch
        token_sym = "DIV"
    elif ch == "<":
        token_str += ch
        ch = input_file.getch()[0]
        if ch == "=":
            token_str += ch
            token_sym = "LEQ"
        else:
            input_file.retract()
            token_sym = "LSS"
    elif ch == ">":
        token_str += ch
        ch = input_file.getch()[0]
        if ch == "=":
            token_str += ch
            token_sym = "GEQ"
        else:
            input_file.retract()
            token_sym = "GRE"
    elif ch == "=":
        token_str += ch
        ch = input_file.getch()[0]
        if ch == "=":
            token_str += ch
            token_sym = "EQL"
        else:
            input_file.retract()
            token_sym = "ASSIGN"
    elif ch == "&":
        token_str += ch
        ch = input_file.getch()[0]
        token_str += ch
        token_sym = "ANDTK"
    elif ch == "|":
        token_str += ch
        ch = input_file.getch()[0]
        token_str += ch
        token_sym = "ANDTK"
    elif ch == ";":
        token_str += ch
        token_sym = "SEMICN"
    elif ch == ",":
        token_str += ch
        token_sym = "COMMA"
    elif ch == "(":
        token_str += ch
        token_sym = "LPARENT"
    elif ch == ")":
        token_str += ch
        token_sym = "RPARENT"
    elif ch == "[":
        token_str += ch
        token_sym = "LBRACK"
    elif ch == "]":
        token_str += ch
        token_sym = "RBRACK"
    elif ch == "{":
        token_str += ch
        token_sym = "LBRACE"
    elif ch == "}":
        token_str += ch
        token_sym = "RBRACE"
    token = Token(line, token_sym, token_str)
    return token

import argparse

from input_file import InputFile
from lexer import get_new_token
from grammar import Grammar


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default=None)
    args = parser.parse_args()
    file = InputFile(args.file)
    token = get_new_token(file)
    # while token:
    #     print(f"{token.token_str} {token.token_sym} {token.line}")
    #     token = get_new_token(file)
    gram = Grammar(file, token)
    gram.program()

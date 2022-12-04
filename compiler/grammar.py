from lexer import get_new_token
from symbol import IntVarSymbol, FltVarSymbol, ArrVarSymbol, \
    VoidFuncSymbol, IntFuncSymbol, FltFuncSymbol, ArrFuncSymbol, BuiltInFuncSymbol


class Grammar(object):

    def __init__(self, file, token):
        self.file = file
        self.subprogram_level = 0  # 分程序层次
        self.subprogram_level_stack = [0]  # 分程序层次栈
        self.token = token
        self.token_stack = []
        self.temp_token_stack = []
        self.name2index_map = dict()
        # key-符号名; value-符号索引列表(不同分程序层次可能有相同的符号名,所以给符号指派了索引)
        self.symbol_list = []
        self._built_in()

    def _built_in(self):
        self._add_arr_var_symbol("gl_Position", 4)
        self._add_arr_var_symbol("gl_FragCoord", 2)
        self._add_arr_var_symbol("iResolution", 2)
        self._add_flt_var_symbol("iTime")
        self._add_built_in_func_symbol("normalize")
        self._add_built_in_func_symbol("cross")
        self._add_built_in_func_symbol("sin")
        self._add_built_in_func_symbol("cos")
        self._add_built_in_func_symbol("abs")
        self._add_built_in_func_symbol("clamp")
        self._add_built_in_func_symbol("fract")
        self._add_built_in_func_symbol("smoothstep")
        self._add_built_in_func_symbol("length")
        self._add_built_in_func_symbol("step")
        self._add_built_in_func_symbol("min")
        self._add_built_in_func_symbol("max")
        self._add_built_in_func_symbol("atan")
        self._add_built_in_func_symbol("reflect")
        self._add_built_in_func_symbol("mix")

    def _get_token(self):
        if len(self.token_stack) > 0:
            token = self.token_stack[-1]
            self.token_stack.pop()
            return token
        else:
            return get_new_token(self.file)

    def _move_stack(self):
        while len(self.temp_token_stack) > 0:
            self.token_stack.append(self.temp_token_stack[-1])
            self.temp_token_stack.pop()

    def _get_into_new_level(self):
        self.subprogram_level += 1
        self.subprogram_level_stack.append(self.subprogram_level)

    def _exit_cur_level(self):
        cur_level = self.subprogram_level_stack[-1]
        self.subprogram_level_stack.pop()
        if len(self.symbol_list) == 0:
            return
        symbol = self.symbol_list[-1]
        while symbol.level == cur_level:
            symbol_name = symbol.name
            index_list = self.name2index_map[symbol_name]
            index_list.pop()
            if len(index_list) == 0:
                # // 如果删除该符号后,发现该作用域外没有该符号,就从name2index_map中删除这个键值对
                self.name2index_map.pop(symbol_name)
            self.symbol_list.pop()
            if len(self.symbol_list) == 0:
                return
            symbol = self.symbol_list[-1]

    def _add_new_symbol2map(self, symbol_name):
        if symbol_name not in self.name2index_map:
            # 如果在name2index_map中不存在这个符号名,那么需要先新建一个键值对
            self.name2index_map[symbol_name] = []
        # 因为symbol_list是从0开始编号的且此时新符号已经添加到其中,
        # 所以添加新符号的索引的时候要添加len(self.symbol_list)-1
        self.name2index_map[symbol_name].append(len(self.symbol_list) - 1)

    def _add_int_var_symbol(self, int_name):
        int_name = int_name.lower()
        int_symbol = IntVarSymbol(int_name, "IntVarSym", self.subprogram_level_stack[-1])
        self.symbol_list.append(int_symbol)
        self._add_new_symbol2map(int_name)

    def _add_flt_var_symbol(self, flt_name):
        flt_name = flt_name.lower()
        flt_symbol = FltVarSymbol(flt_name, "FltVarSym", self.subprogram_level_stack[-1])
        self.symbol_list.append(flt_symbol)
        self._add_new_symbol2map(flt_name)

    def _add_arr_var_symbol(self, arr_name, arr_dim_1, arr_dim_2=None, in_out_type=None):
        arr_name = arr_name.lower()
        arr_symbol = ArrVarSymbol(arr_name, "ArrVarSym", self.subprogram_level_stack[-1], arr_dim_1, arr_dim_2, in_out_type)
        self.symbol_list.append(arr_symbol)
        self._add_new_symbol2map(arr_name)

    def _add_void_func_symbol(self, func_name):
        func_name = func_name.lower()
        func_symbol = VoidFuncSymbol(func_name, "VoidFuncSym", self.subprogram_level_stack[-1])
        self.symbol_list.append(func_symbol)
        self._add_new_symbol2map(func_name)

    def _add_int_func_symbol(self, func_name):
        func_name = func_name.lower()
        func_symbol = IntFuncSymbol(func_name, "IntFuncSym", self.subprogram_level_stack[-1])
        self.symbol_list.append(func_symbol)
        self._add_new_symbol2map(func_name)

    def _add_flt_func_symbol(self, func_name):
        func_name = func_name.lower()
        func_symbol = FltFuncSymbol(func_name, "FltFuncSym", self.subprogram_level_stack[-1])
        self.symbol_list.append(func_symbol)
        self._add_new_symbol2map(func_name)

    def _add_arr_func_symbol(self, func_name, arr_dim_1, arr_dim_2=None):
        func_name = func_name.lower()
        func_symbol = ArrFuncSymbol(func_name, "ArrFuncSym", self.subprogram_level_stack[-1], arr_dim_1, arr_dim_2)
        self.symbol_list.append(func_symbol)
        self._add_new_symbol2map(func_name)

    def _add_built_in_func_symbol(self, func_name):
        func_name = func_name.lower()
        func_symbol = BuiltInFuncSymbol(func_name, "BuiltInFuncSym", 0)
        self.symbol_list.append(func_symbol)
        self._add_new_symbol2map(func_name)

    def _get_symbol_latest(self, symbol_name):
        symbol_name = symbol_name.lower()
        if symbol_name not in self.name2index_map:
            return None
        index_list = self.name2index_map[symbol_name]
        if len(index_list) == 0:
            return None
        return self.symbol_list[index_list[-1]]

    def _get_symbol_latest_type(self, symbol_name):
        symbol_name = symbol_name.lower()
        if symbol_name not in self.name2index_map:
            return "OtherTypeSym"
        index_list = self.name2index_map[symbol_name]
        if len(index_list) == 0:
            return "OtherTypeSym"
        return self.symbol_list[index_list[-1]].type

    def _is_var_declaration(self):
        if self.token.token_sym != "INTTK" and self.token.token_sym != "FLTTK" and self.token.token_sym != "ARRTK":
            return False
        if self.token.token_sym == "ARRTK":
            for _ in range(4):
                token = self._get_token()
                self.temp_token_stack.append(token)
            if self.temp_token_stack[-1].token_sym == "LBRACK":
                for _ in range(3):
                    token = self._get_token()
                    self.temp_token_stack.append(token)
            token = self._get_token()  # ; or (
            self.temp_token_stack.append(token)
        else:
            for _ in range(2):
                token = self._get_token()
                self.temp_token_stack.append(token)
        if self.temp_token_stack[-1].token_sym == "LPARENT":  # 函数定义
            self._move_stack()
            return False
        self._move_stack()
        return True

    def _is_var_def_with_init(self):
        self.temp_token_stack.append(self._get_token())
        while self.temp_token_stack[-1].token_sym != "COMMA" and self.temp_token_stack[-1].token_sym != "SEMICN":
            if self.temp_token_stack[-1].token_sym == "ASSIGN":
                self._move_stack()
                return True
            self.temp_token_stack.append(self._get_token())
        self._move_stack()
        return False

    def _is_func_def(self):
        if self.token.token_sym != "INTTK" and self.token.token_sym != "FLTTK" and \
            self.token.token_sym != "ARRTK" and self.token.token_sym != "VOIDTK":
            return False
        if self.token.token_sym == "ARRTK":
            for _ in range(4):
                self.temp_token_stack.append(self._get_token())
            if self.temp_token_stack[-1].token_sym == "LBRACK":
                for _ in range(3):
                    self.temp_token_stack.append(self._get_token())
            self.temp_token_stack.append(self._get_token())
        else:
            self.temp_token_stack.append(self._get_token())
            if self.temp_token_stack[-1].token_sym != "IDENFR":
                self._move_stack()
                return False
            self.temp_token_stack.append(self._get_token())
        if self.temp_token_stack[-1].token_sym != "LPARENT":
            self._move_stack()
            return False
        self._move_stack()
        return True

    def _is_statement(self):
        return self.token.token_sym == "IDENFR" or self.token.token_sym == "WHILETK" or self.token.token_sym == "IFTK" or \
            self.token.token_sym == "SEMICN" or self.token.token_sym == "RETURNTK" or self.token.token_sym == "LBRACE" or \
                self.token.token_sym == "BRKTK"

    def _is_func_call(self):
        if self.token.token_sym != "IDENFR":
            return False
        self.temp_token_stack.append(self._get_token())
        if self.temp_token_stack[-1].token_sym != "LPARENT":
            self._move_stack()
            return False
        self._move_stack()
        return True

    def _is_func_call_with_ret(self):
        func_name = self.token.token_str.lower()
        return self._get_symbol_latest_type(func_name) != "VoidFuncSym"

    def _is_expr(self):
        token_sym = self.token.token_sym
        return token_sym == "PLUS" or token_sym == "MINU" or \
            token_sym == "IDENFR" or token_sym == "LPARENT" or \
                token_sym == "INTCON" or token_sym == "FLTCON"

    # <输入输出定义> ::= in <类型标识符> <标识符> | out <类型标识符> <标识符>
    def _in_out_def(self):
        in_out_type = self.token.token_sym
        self.token = self._get_token()  # array
        if self.token.token_sym == "ARRTK":
            self.token = self._get_token()  # [
            self.token = self._get_token()  # arr_dim_1
            arr_dim_1 = int(self.token.token_str)
            self.token = self._get_token()  # ]
            self.token = self._get_token()  # IDENFR
            self._add_arr_var_symbol(self.token.token_str, arr_dim_1, None, in_out_type)
            self.token = self._get_token()  # ;

    # <输入输出说明> ::= <输入输出定义>; {<输入输出定义>;}
    def _in_out_declaration(self):
        self._in_out_def()
        self.token = self._get_token()
        while self.token.token_sym == "INTK" or self.token.token_sym == "OUTTK":
            self._in_out_def()
            self.token = self._get_token()

    # <常量> ::= <整数> | <小数>
    def _const_sym(self):
        token_value = 0
        if self.token.token_sym == "PLUS":
            self.token = self._get_token()
            token_value = float(self.token.token_str)
        elif self.token.token_sym == "MINU":
            self.token = self._get_token()
            token_value = -float(self.token.token_str)
        else:
            token_value = float(self.token.token_str)
        return token_value

    '''
    <变量定义及初始化> ::= <类型标识符> <标识符> = <常量>;
        | <类型标识符> <标识符> = '{'<常量>{, <常量>}'}';
        | <类型标识符> <标识符> = '{''{'<常量>{, <常量>}'}'{, '{'<常量>{, <常量>}'}'}'}';
    '''
    def _var_def_with_init(self):
        symbol_type_sym = self.token.token_sym
        # expr_type
        if symbol_type_sym == "ARRTK":
            self.token = self._get_token()  # [
            self.token = self._get_token()  # arr_dim_1
            arr_dim_1 = int(self.token.token_str)
            self.token = self._get_token()  # ]
            self.token = self._get_token()  # IDENFR or [
            arr_dim_2 = None
            arr_name = self.token.token_str
            if self.token.token_sym != "LBRACK":
                # array'['<无符号整数>']' <标识符> = '{'<常量>{, <常量>}'}'
                self.token = self._get_token()  # =
                self.token = self._get_token()  # {
                self.token = self._get_token()
                const_value = self._const_sym()
                for _ in range(arr_dim_1 - 1):
                    self.tokne = self._get_token()  # ,
                    self.token = self._get_token()
                    const_value = self._const_sym()
                self.token = self._get_token()  # }
            else:
                # array'['<无符号整数>']''['<无符号整数>']' <标识符> = '{''{'<常量>{, <常量>}'}'{, '{'<常量>{, <常量>}'}'}'}'
                self.token = self._get_token()  # arr_dim_2
                arr_dim_2 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # IDENFR
                arr_name = self.token.token_str
                self.token = self._get_token()  # =

                self.token = self._get_token()  # {
                self.token = self._get_token()  # {
                self.token = self._get_token()
                const_value = self._const_sym()
                for _ in range(arr_dim_2 - 1):
                    self.token = self._get_token()  # ,
                    self.token = self._get_token()
                    const_value = self._const_sym()
                self.token = self._get_token()  # }
                for _ in range(arr_dim_1 - 1):
                    self.token = self._get_token()  # ,
                    self.token = self._get_token()  # {
                    self.token = self._get_token()
                    const_value = self._const_sym()
                    for _ in range(arr_dim_2 - 1):
                        self.token = self._get_token()  # ,
                        self.token = self._get_token()
                        const_value = self._const_sym()
                    self.token = self._get_token()  # }
                self.token = self._get_token()  # }
            self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
        elif symbol_type_sym == "INTTK":
            # int <标识符> = <常量>
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_int_var_symbol(symbol_name)
            self.token = self._get_token()  # =
            self.token = self._get_token()
            const_value = self._const_sym()
        else:
            # float <标识符> = <常量>
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_flt_var_symbol(symbol_name)
            self.token = self._get_token()  # =
            self.token = self._get_token()
            const_value = self._const_sym()
        self.token = self._get_token()  # ;

    # <变量定义无初始化> ::= <类型标识符> <标识符>{, <标识符>};
    def _var_def_no_init(self):
        symbol_type_sym = self.token.token_sym
        if symbol_type_sym == "ARRTK":
            self.token = self._get_token()  # [
            self.token = self._get_token()  # arr_dim_1
            arr_dim_1 = int(self.token.token_str)
            self.token = self._get_token()  # ]
            self.token = self._get_token()  # IDENFR or [
            if self.token.token_sym != "LBRACK":
                # array'['<无符号整数>']' <标识符>{, <标识符>};
                arr_name = self.token.token_str
                self._add_arr_var_symbol(arr_name, arr_dim_1)
                self.token = self._get_token()  # , or ;
                while self.token.token_sym == "COMMA":
                    self.token = self._get_token()  # IDENFR
                    arr_name = self.token.token_str
                    self._add_arr_var_symbol(arr_name, arr_dim_1)
                    self.token = self._get_token()  # , or ;
            else:
                # array'['<无符号整数>']''['<无符号整数>']' <标识符>{, <标识符>};
                self.token = self._get_token()  # arr_dim_2
                arr_dim_2 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # IDENFR
                arr_name = self.token.token_str
                self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                self.token = self._get_token()  # , or ;
                while self.token.token_sym == "COMMA":
                    self.token = self._get_token()  # IDENFR
                    arr_name = self.token.token_str
                    self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                    self.token = self._get_token()  # , or ;
        elif symbol_type_sym == "INTTK":
            # int <标识符>{, <标识符>};
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_int_var_symbol(symbol_name)
            self.token = self._get_token()  # , or ;
            while self.token.token_sym == "COMMA":
                self.token = self._get_token()  # IDENFR
                symbol_name = self.token.token_str
                self._add_int_var_symbol(symbol_name)
                self.token = self._get_token()  # , or ;
        else:
            # float <标识符>{, <标识符>};
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_flt_var_symbol(symbol_name)
            self.token = self._get_token()  # , or ;
            while self.token.token_sym == "COMMA":
                self.token = self._get_token()  # IDENFR
                symbol_name = self.token.token_str
                self._add_flt_var_symbol(symbol_name)
                self.token = self._get_token()  # , or ;       

    # <变量定义> ::= <变量定义无初始化> | <变量定义及初始化>
    def _var_def(self):
        if self._is_var_def_with_init():
            self._var_def_with_init()
        else:
            self._var_def_no_init()

    # <变量说明> ::= <变量定义>; {<变量定义>;}
    def _var_declaration(self):
        self._var_def()  # ;
        self.token = self._get_token()
        while self._is_var_declaration():
            self._var_def()  # ;
            self.token = self._get_token()

    # <参数表> ::= <类型标识符> <标识符>{, <类型标识符> <标识符>} | <空>
    def _para_tlb(self):
        func_symbol = self.symbol_list[-1]
        if self.token.token_sym == "INTTK":
            self.token = self._get_token()  # IDENFR
            self._add_int_var_symbol(self.token.token_str)
            self.token = self._get_token()  # , or )
        elif self.token.token_sym == "FLTTK":
            self.token = self._get_token()  # IDENFR
            self._add_flt_var_symbol(self.token.token_str)
            self.token = self._get_token()  # , or )
        elif self.token.token_sym == "ARRTK":
            self.token = self._get_token()  # [
            self.token = self._get_token()  # arr_dim_1
            arr_dim_1 = int(self.token.token_str)
            self.token = self._get_token()  # ]
            self.token = self._get_token()  # [ or IDENFR
            arr_dim_2 = None
            arr_name = self.token.token_str
            if self.token.token_sym == "LBRACK":
                self.token = self._get_token()  # arr_dim_2
                arr_dim_2 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # IDENFR
                arr_name = self.token.token_str
            self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
            self.token = self._get_token()  # , or )
        while self.token.token_sym == "COMMA":
            self.token = self._get_token()
            if self.token.token_sym == "INTTK":
                self.token = self._get_token()  # IDENFR
                self._add_int_var_symbol(self.token.token_str)
                self.token = self._get_token()  # , or )
            elif self.token.token_sym == "FLTTK":
                self.token = self._get_token()  # IDENFR
                self._add_flt_var_symbol(self.token.token_str)
                self.token = self._get_token()  # , or )
            elif self.token.token_sym == "ARRTK":
                self.token = self._get_token()  # [
                self.token = self._get_token()  # arr_dim_1
                arr_dim_1 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # [ or IDENFR
                arr_dim_2 = None
                arr_name = self.token.token_str
                if self.token.token_sym == "LBRACK":
                    self.token = self._get_token()  # arr_dim_2
                    arr_dim_2 = int(self.token.token_str)
                    self.token = self._get_token()  # ]
                    self.token = self._get_token()  # IDENFR
                    arr_name = self.token.token_str
                self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                self.token = self._get_token()  # , or )

    # <无返回值函数定义> ::= void <标识符> '('<参数表>')''{'<复合语句>'}'
    def _func_def_no_ret(self):
        self.token = self._get_token()  # IDENFR
        func_name = self.token.token_str
        self._add_void_func_symbol(func_name, "VoidFuncSym", self.subprogram_level_stack[-1])
        self.token = self._get_token()  # (
        self._get_into_new_level()
        self.token = self._get_token()
        self.token = self._para_tlb()  # )
        self.token = self._get_token()  # {
        self.token = self._get_token()
        self._compound_statements()  # }
        self.token = self._get_token()
        self._exit_cur_level()

    # <声明头部> ::= <类型标识符> <标识符>
    def _declaration_head(self):
        if self.token.token_sym == "INTTK":
            self.token = self._get_token()  # IDENFR
            self._add_int_func_symbol(self.token.token_str)
        elif self.token.token_sym == "FLTTK":
            self.token = self._get_token()  # IDENFR
            self._add_flt_func_symbol(self.token.token_str)
        elif self.token.token_sym == "ARRTK":
            self.token = self._get_token()  # [
            self.token = self._get_token()  # arr_dim_1
            arr_dim_1 = int(self.token.token_str)
            self.token = self._get_token()  # ]
            self.token = self._get_token()  # [ or IDENFR
            arr_dim_2 = None
            if self.token.token_sym == "LBRACK":
                self.token = self._get_token()  # arr_dim_2
                arr_dim_2 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # IDENFR
            self._add_arr_func_symbol(self.token.token_str, arr_dim_1, arr_dim_2)
        self.token = self._get_token()  # (

    # <有返回值函数定义> ::= <声明头部>'('<参数表>')''{'<复合语句>'}'
    def _func_def_with_ret(self):
        self._declaration_head()  # (
        self._get_into_new_level()
        self.token = self._get_token()
        self._para_tlb()  # )
        self.token = self._get_token()  # {
        self.token = self._get_token()
        self._compound_statements()  # }
        self.token = self._get_token()
        self._exit_cur_level()

    # <复合语句> ::=[<变量说明>] <语句列>
    def _compound_statements(self):
        if self.token.token_sym == "INTTK" or self.token.token_sym == "FLTTK" or self.token.token_sym == "ARRTK":
            self._var_declaration()
        self._statement_list()

    # <语句列> ::= {<语句>}
    def _statement_list(self):
        while self._is_statement():
            self._statement()

    '''
    <语句> ::= <循环语句> | <条件语句> | <赋值语句>; | <有返回值函数调用语句>;
        | <无返回值函数调用语句>; | <空>; | <返回语句>; | '{'<语句列>'}' | break;
    '''
    def _statement(self):
        if self.token.token_sym == "WHILETK":
            self._loop_statement()
        elif self.token.token_sym == "IFTK":
            self._condition_statement()
        elif self._is_func_call():
            if self._is_func_call_with_ret():
                self._func_call_with_ret()
            else:
                self._func_call_no_ret()
            self.token = self._get_token()
        elif self.token.token_sym == "IDENFR":
            self._assign_statement()
            self.token = self._get_token()
        elif self.token.token_sym == "SEMICN":
            self.token = self._get_token()
        elif self.token.token_sym == "RETURNTK":
            self._ret_statement()
            self.token = self._get_token()
        elif self.token.token_sym == "LBRACE":
            self.token = self._get_token()
            self._statement_list()  # }
            self.token = self._get_token()
        elif self.token.token_sym == "BRKTK":
            self.token = self._get_token()  # ;
            self.token = self._get_token()

    # <循环语句> ::= while '('<条件>')' <语句>
    def _loop_statement(self):
        self.token = self._get_token()  # (
        self.token = self._get_token()
        self._condition()  # )
        self.token = self._get_token()
        self._statement()

    # <条件语句> ::= if '('<条件>')' <语句> [else <语句>]
    def _condition_statement(self):
        self.token = self._get_token()  # (
        self.token = self._get_token()
        self._condition()  # )
        self.token = self._get_token()
        self._statement()
        if self.token.token_sym == "ELSETK":
            self.token = self._get_token()
            self._statement()

    # <条件> ::= <条件项>{<条件运算符><条件项>}
    def _condition(self):
        self._condition_term()  # 条件运算符 or )
        while self.token.token_sym == "ANDTK" or self.token.token_sym == "ORTK":
            condition_sym = self.token.token_sym
            self.token = self._get_token()
            self._condition_term()

    # <条件项> ::= <表示式><关系运算符><表达式> | '('<条件>')'
    def _condition_term(self):
        if self.token.token_sym == "LPARENT":
            # example中不会出现
            self.token = self._get_token()
            self._condition()  # )
            self.token = self._get_token()
        else:
            self._expr()  # 关系运算符
            relation_sym = self.token.token_sym
            self.token = self._get_token()
            self._expr()

    # <有返回值函数调用语句> ::= <标识符>'('<值参数表>')'
    def _func_call_with_ret(self):
        func_name = self.token.token_str.lower()
        self.token = self._get_token()  # (
        self.token = self._get_token()  # ) or IDENFR
        self._value_para_tlb()  # )
        self.token = self._get_token()  # ;

    # <无返回值函数调用语句> ::= <标识符>'('<值参数表>')'
    def _func_call_no_ret(self):
        func_name = self.token.token_str.lower()
        self.token = self._get_token()  # (
        self.token = self._get_token()  # ) or IDENFR
        self._value_para_tlb()  # )
        self.token = self._get_token()  # ;

    # <值参数表> ::= <表达式>{, <表达式>} | <空>
    def _value_para_tlb(self):
        if self._is_expr():
            self._expr()
            while self.token.token_sym == "COMMA":
                self.token = self._get_token()
                self._expr()

    # <返回语句> ::= return [<表达式>]
    def _ret_statement(self):
        self.token = self._get_token()
        if self.token.token_sym != "SEMICN":
            self._expr()

    '''
    <赋值语句> ::= <标识符> = <表达式>
        | <标识符> = '{'<表达式>{, <表达式>}'}' 
        | <标识符> = '{''{'<表达式>{, <表达式>}'}'{, '{'<表达式>{, <表达式>}'}'}'}'
        | <标识符>'['<表达式>']' = <表达式>
        | <标识符>'['<表达式>']''['<表达式>']' = <表达式> 
    '''
    def _assign_statement(self):
        symbol_name = self.token.token_str.lower()
        self.token = self._get_token()  # = or [
        if self.token.token_sym == "ASSIGN":
            self.token = self._get_token()
            if self.token.token_sym == "LBRACE":
                symbol = self._get_symbol_latest(symbol_name)
                if symbol.arr_dim_2:
                    # <标识符> = '{''{'<表达式>{, <表达式>}'}'{, '{'<表达式>{, <表达式>}'}'}'}';
                    self.token = self._get_token()  # {
                    self.token = self._get_token()
                    for _ in range(symbol.arr_dim_2):
                        self._expr()  # , or }
                        self.token = self._get_token()
                    for _ in range(symbol.arr_dim_1 - 1):
                        self.token = self._get_token()  # {
                        self.token = self._get_token()
                        for _ in range(symbol.arr_dim_2):
                            self._expr()  # , or }
                            self.token = self._get_token()
                    self.token = self._get_token()  # ;
                else:
                    # <标识符> = '{'<表达式>{, <表达式>}'}';
                    self.token = self._get_token()
                    for _ in range(symbol.arr_dim_1):
                        self._expr()  # , or }
                        self.token = self._get_token()
            else:
                self._expr()  # ;
        else:
            symbol = self._get_symbol_latest(symbol_name)
            self._expr()  # ]
            self.token = self._get_token()  # = or [
            if self.token.token_sym == "ASSIGN":
                self.token = self._get_token()
                self._expr()  # ;
            else:
                self.token = self._get_token()
                self._expr()  # ]
                self.token = self._get_token()  # =
                self.token = self._get_token()
                self._expr()  # ;

    # <表达式> ::= [ + | - ]<项>{<加法运算符><项>}
    def _expr(self):
        is_first_sym_minu = False
        if self.token.token_sym == "PLUS" or self.token.token_sym == "MINU":
            if self.token.token_sym == "MINU":
                is_first_sym_minu = True
            self.token = self._get_token()
        self._term()
        if is_first_sym_minu:
            pass
        while self.token.token_sym == "PLUS" or self.token.token_sym == "MINU":
            self.token = self._get_token()
            self._term()

    # <项> ::= <因子>{<乘法运算符><因子>}
    def _term(self):
        self._factor()
        while self.token.token_sym == "MULT" or self.token.token_sym == "DIV":
            self.token = self._get_token()
            self._factor()

    '''
    <因子> ::= <标识符> | <标识符>'['<表达式>']' | <标识符>'['<表达式']''['<表达式']'
        | '('<表达式>')' | <整数> | <小数> | <有返回值函数调用语句>
    '''
    def _factor(self):
        if self._is_func_call():
            # <有返回值函数调用语句>
            func_name = self.token.token_str.lower()
            self._func_call_with_ret()
        elif self.token.token_sym == "IDENFR":
            symbol_name = self.token.token_str
            symbol = self._get_symbol_latest(symbol_name)
            self.token = self._get_token()
            if self.token.token_sym == "LBRACK":
                self.token = self._get_token()
                self._expr()  # ]
                self.token = self._get_token()
                if self.token.token_sym == "LBRACK":
                    self.token = self._get_token()
                    self._expr()
                    self.token = self._get_token()
        elif self.token.token_sym == "LPARENT":
            self.token = self._get_token()
            self._expr()  # )
            self.token = self._get_token()
        elif self.token.token_sym == "PLUS" or self.token.token_sym == "MINU" or \
            self.token.token_sym == "INTCON" or self.token.token_sym == "FLTCON":
            const_value = self._const_sym()
            self.token = self._get_token()

    def _main_func(self):
        self.token = self._get_token()  # main
        self.token = self._get_token()  # (
        self.token = self._get_token()  # )
        self.token = self._get_token()  # {
        self.token = self._get_token()
        self._get_into_new_level()
        self._compound_statements()
        self._exit_cur_level()
        self.token = self._get_token()

    def program(self):
        if self.token.token_sym == "INTK" or self.token.token_sym == "OUTTK":
            self._in_out_declaration()
        if self._is_var_declaration():
            self._var_declaration()
        while self._is_func_def():
            if self.token.token_sym == "VOIDTK":
                self._func_def_no_ret()
            else:
                self._func_def_with_ret()
        self._main_func()
        print(self.token)
        self._exit_cur_level()

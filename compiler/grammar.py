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
        # spri-v code
        self.spirv_list_opnames = []
        self.spirv_list_defines = []
        self.spirv_list_funcs = []
        self.tmp_index = 200
        self.opnames = {}
        self.defines = []
        self.func_dict = {}
        self.id_dict = {}
        self.func_opvariable_index = 0
        # build_in
        self.build_in_vars = {'gl_Position': 'v4float', 'gl_FragCoord': 'v4float', 'iResolution': 'v3float', 
                            'iTime': 'float', 'frag_pos': 'v2float', 'out_color': 'v4float', 
                            'fragcoord': 'v2float', 'ufragcolor': 'v4float'}
        self.build_in_funcs = ['normalize', 'cross', 'sin', 'cos', 'abs', 'clamp', 'fract', 
                            'smoothstep', 'length', 'step', 'min', 'max', 'atan', 'reflect', 'mix']
        self.build_in_templates = []     
        self._built_in()
        self._built_in_template()

    def _built_in(self):
        self._add_arr_var_symbol("gl_Position", 4, build_in=True)
        self._add_arr_var_symbol("gl_FragCoord", 2, build_in=True)
        self._add_arr_var_symbol("iResolution", 2, build_in=True)
        self._add_flt_var_symbol("iTime", build_in=True)
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
    
    def _built_in_template(self):
        with open('./spvasm_templates/main.frag_template.spvasm', encoding='utf-8') as f:
            self.build_in_templates = f.readlines()
        f.close()
        # with open('main.vert_template.spvasm', encoding='utf-8') as f:
        #     self.build_in_templates = f.readlines()
        # f.close()
    
    def _find_defined_type(self, name):
        for str in self.build_in_templates:
            if str.find(name) != -1:
                return True
        for str in self.spirv_list_defines:
            if str.find(name) != -1:
                return True
        return False
    
    def _get_temp(self):
        self.tmp_index += 1
        return f'%{self.tmp_index-1}'
    
    def _get_cur_temp(self):
        return f'%{self.tmp_index}'

    def _add_spirv_list_opname(self, spirv):
        self.spirv_list_opnames.append(spirv + '\n')

    def _add_spirv_list_define(self, spirv):
        self.spirv_list_defines.append(spirv + '\n')

    def _add_spirv_list_func(self, spirv):
        self.spirv_list_funcs.append(spirv + '\n')
    
    def _add_spirv_func_variable(self, spirv):
        self.spirv_list_funcs.insert(self.func_opvariable_index, spirv)
        self.func_opvariable_index += 1

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

    def _add_new_opnames(self, name):
        if name not in self.opnames:
            self.opnames[name] = 0
        self.opnames[name] += 1
    
    def _add_spirv_opname(self, name):
        opname = ''
        if name in self.build_in_vars:
            return '%' + name
        if (self.opnames[name] <= 1):
            opname = '%' + name
        else:
            opname = '%' + name + '_' + str(self.opnames[name]-2)
        self._add_spirv_list_opname(f'OpName {opname} \"{name}\"')
        return opname
    
    def _add_id_dict(self, name, opname, type):
        if name in self.build_in_vars:
            return
        self.id_dict[(name, self.subprogram_level_stack[-1])] = (opname, type)

    def _get_id_info(self, name):
        if name in self.build_in_vars:
            return ('%' + name, self.build_in_vars[name])
        return self.id_dict[(name, self.subprogram_level_stack[-1])]
        
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

    def _add_flt_var_symbol(self, flt_name, build_in=False):
        flt_name = flt_name.lower()
        flt_symbol = FltVarSymbol(flt_name, "FltVarSym", self.subprogram_level_stack[-1])
        self.symbol_list.append(flt_symbol)
        self._add_new_symbol2map(flt_name)

    def _add_arr_var_symbol(self, arr_name, arr_dim_1, arr_dim_2=None, in_out_type=None, build_in=False):
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
                floatname = ''
                if const_value >= 0:
                    floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                else:
                    floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                if not self._find_defined_type(floatname):
                    self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
                floatnames = [floatname]
                self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                self._add_new_opnames(arr_name)
                opname = self._add_spirv_opname(arr_name)
                self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_v{arr_dim_1}float Function')
                self._add_id_dict(arr_name, opname, f'v{arr_dim_1}float')
                for _ in range(arr_dim_1 - 1):
                    self.tokne = self._get_token()  # ,
                    self.token = self._get_token()
                    const_value = self._const_sym()
                    if const_value >= 0:
                        floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                    else:
                        floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                    if not self._find_defined_type(floatname):
                        self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
                    floatnames.append(floatname)
                tmp = self._get_temp()
                floatname_str = ''
                for i in floatnames:
                    floatname_str += i + ' '
                self._add_spirv_list_define(f'{tmp} = OpConstantComposite %v{arr_dim_1}float ' + floatname_str)
                self._add_spirv_list_func(f'OpStore {opname} {tmp}')
                self.token = self._get_token()  # }
            # todo
            else:
                # array'['<无符号整数>']''['<无符号整数>']' <标识符> = '{''{'<常量>{, <常量>}'}'{, '{'<常量>{, <常量>}'}'}'}'
                self.token = self._get_token()  # arr_dim_2
                arr_dim_2 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # IDENFR
                arr_name = self.token.token_str
                self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                self._add_new_opnames(arr_name)
                opname = self._add_spirv_opname(arr_name)
                self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_mat{arr_dim_1}v{arr_dim_2}float Function')
                self._add_id_dict(arr_name, opname, 'mat{arr_dim_1}v{arr_dim_2}float')
                self.token = self._get_token()  # =
                self.token = self._get_token()  # {
                self.token = self._get_token()  # {
                self.token = self._get_token()
                const_value = self._const_sym()
                floatname = ''
                if const_value >= 0:
                    floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                else:
                    floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                if not self._find_defined_type(floatname):
                    self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
                floatnames = [floatname]
                for _ in range(arr_dim_2 - 1):
                    self.token = self._get_token()  # ,
                    self.token = self._get_token()
                    const_value = self._const_sym()
                    if const_value >= 0:
                        floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                    else:
                        floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                    if not self._find_defined_type(floatname):
                        self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
                    floatnames.append(floatname)
                tmp = self._get_temp()
                floatname_str = ''
                for i in floatnames:
                    floatname_str += i + ' '
                self._add_spirv_list_define(f'{tmp} = OpConstantComposite %v{arr_dim_2}float ' + floatname_str)
                tmps = [tmp]
                self.token = self._get_token()  # }
                for _ in range(arr_dim_1 - 1):
                    self.token = self._get_token()  # ,
                    self.token = self._get_token()  # {
                    self.token = self._get_token()
                    const_value = self._const_sym()
                    if const_value >= 0:
                        floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                    else:
                        floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                    if not self._find_defined_type(floatname):
                        self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
                    floatnames = [floatname]
                    for _ in range(arr_dim_2 - 1):
                        self.token = self._get_token()  # ,
                        self.token = self._get_token()
                        const_value = self._const_sym()
                        if const_value >= 0:
                            floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                        else:
                            floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                        if not self._find_defined_type(floatname):
                            self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
                        floatnames.append(floatname)
                    tmp = self._get_temp()
                    floatname_str = ''
                    for i in floatnames:
                        floatname_str += i + ' '
                    self._add_spirv_list_define(f'{tmp} = OpConstantComposite %v{arr_dim_2}float ' + floatname_str)
                    tmps.append(tmp)    
                    self.token = self._get_token()  # }
                self.token = self._get_token()  # }
                tmp = self._get_temp()
                tmpnames_str = ''
                for i in tmps:
                    tmpnames_str += i + ' '
                self._add_spirv_list_define(f'{tmp} = OpConstantComposite %mat{arr_dim_1}v{arr_dim_2}float ' + tmpnames_str)
                self._add_spirv_list_func(f'OpStore {opname} {tmp}')
                self.token = self._get_token()  # }
        elif symbol_type_sym == "INTTK":
            # int <标识符> = <常量>
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_int_var_symbol(symbol_name)
            self._add_new_opnames(symbol_name)
            opname = self._add_spirv_opname(symbol_name)
            self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_int Function')
            self._add_id_dict(symbol_name, opname, 'int')
            self.token = self._get_token()  # =
            self.token = self._get_token()
            const_value = self._const_sym()
            intname = ''
            if const_value >= 0:
                intname = f'%int_{int(const_value)}'
            else:
                intname = f'%int_n{-int(const_value)}'
            if not self._find_defined_type(intname):
                self._add_spirv_list_define(f'{intname} = OpConstant %int {int(const_value)}')
            self._add_spirv_list_func(f'OpStore {opname} {intname}')
        else:
            # float <标识符> = <常量>
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_flt_var_symbol(symbol_name)
            self._add_new_opnames(symbol_name)
            opname = self._add_spirv_opname(symbol_name)
            self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_float Function')
            self._add_id_dict(symbol_name, opname, 'float')
            self.token = self._get_token()  # =
            self.token = self._get_token()
            const_value = self._const_sym()
            floatname = ''
            if const_value >= 0:
                floatname = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
            else:
                floatname = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
            if not self._find_defined_type(floatname):
                self._add_spirv_list_define(f'{floatname} = OpConstant %float {const_value}')
            self._add_spirv_list_func(f'OpStore {opname} {floatname}')
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
                self._add_new_opnames(arr_name)
                opname = self._add_spirv_opname(arr_name)
                self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_v{arr_dim_1}float Function')
                self._add_id_dict(arr_name, opname, f'v{arr_dim_1}float')
                self.token = self._get_token()  # , or ;
                while self.token.token_sym == "COMMA":
                    self.token = self._get_token()  # IDENFR
                    arr_name = self.token.token_str
                    self._add_arr_var_symbol(arr_name, arr_dim_1)
                    self._add_new_opnames(arr_name)
                    opname = self._add_spirv_opname(arr_name)
                    self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_v{arr_dim_1}float Function')
                    self._add_id_dict(arr_name, opname, f'v{arr_dim_1}float')
                    self.token = self._get_token()  # , or ;
            else:
                # array'['<无符号整数>']''['<无符号整数>']' <标识符>{, <标识符>};
                self.token = self._get_token()  # arr_dim_2
                arr_dim_2 = int(self.token.token_str)
                self.token = self._get_token()  # ]
                self.token = self._get_token()  # IDENFR
                arr_name = self.token.token_str
                self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                self._add_new_opnames(arr_name)
                opname = self._add_spirv_opname(arr_name)
                self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_mat{arr_dim_1}v{arr_dim_2}float Function')
                self._add_id_dict(arr_name, opname, 'mat{arr_dim_1}v{arr_dim_2}float')
                self.token = self._get_token()  # , or ;
                while self.token.token_sym == "COMMA":
                    self.token = self._get_token()  # IDENFR
                    arr_name = self.token.token_str
                    self._add_arr_var_symbol(arr_name, arr_dim_1, arr_dim_2)
                    self._add_new_opnames(arr_name)
                    opname = self._add_spirv_opname(arr_name)
                    self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_mat{arr_dim_1}v{arr_dim_2}float Function')
                    self._add_id_dict(arr_name, opname, 'mat{arr_dim_1}v{arr_dim_2}float')
                    self.token = self._get_token()  # , or ;
        elif symbol_type_sym == "INTTK":
            # int <标识符>{, <标识符>};
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_int_var_symbol(symbol_name)
            self._add_new_opnames(symbol_name)
            opname = self._add_spirv_opname(symbol_name)
            self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_int Function')
            self._add_id_dict(symbol_name, opname, 'int')
            self.token = self._get_token()  # , or ;
            while self.token.token_sym == "COMMA":
                self.token = self._get_token()  # IDENFR
                symbol_name = self.token.token_str
                self._add_int_var_symbol(symbol_name)
                self._add_new_opnames(symbol_name)
                opname = self._add_spirv_opname(symbol_name)
                self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_int Function')
                self._add_id_dict(symbol_name, opname, 'int')
                self.token = self._get_token()  # , or ;
        else:
            # float <标识符>{, <标识符>};
            self.token = self._get_token()  # IDENFR
            symbol_name = self.token.token_str
            self._add_flt_var_symbol(symbol_name)
            self._add_new_opnames(symbol_name)
            opname = self._add_spirv_opname(symbol_name)
            self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_float Function')
            self._add_id_dict(symbol_name, opname, 'float')
            self.token = self._get_token()  # , or ;
            while self.token.token_sym == "COMMA":
                self.token = self._get_token()  # IDENFR
                symbol_name = self.token.token_str
                self._add_flt_var_symbol(symbol_name)
                self._add_new_opnames(symbol_name)
                opname = self._add_spirv_opname(symbol_name)
                self._add_spirv_func_variable(f'{opname} = OpVariable %_ptr_Function_float Function')
                self._add_id_dict(symbol_name, opname, 'float')
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
        para_tlb = {}
        func_symbol = self.symbol_list[-1]
        if self.token.token_sym == "INTTK":
            self.token = self._get_token()  # IDENFR
            self._add_int_var_symbol(self.token.token_str)
            self._add_new_opnames(self.token.token_str)
            opname = self._add_spirv_opname(self.token.token_str)
            self._add_id_dict(self.token.token_str, opname, 'int')
            para_tlb[f'{self.token.token_str}'] = f'int'
            self.token = self._get_token()  # , or )
        elif self.token.token_sym == "FLTTK":
            self.token = self._get_token()  # IDENFR
            self._add_flt_var_symbol(self.token.token_str)
            self._add_new_opnames(self.token.token_str)
            opname = self._add_spirv_opname(self.token.token_str)
            self._add_id_dict(self.token.token_str, opname, 'float')
            para_tlb[f'{self.token.token_str}'] = f'float'
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
            self._add_new_opnames(self.token.token_str)
            opname = self._add_spirv_opname(self.token.token_str)
            if (arr_dim_2 == None):
                para_tlb[f'{arr_name}'] = f'v{arr_dim_1}float'
                self._add_id_dict(self.token.token_str, opname, f'v{arr_dim_1}float')
            else:
                para_tlb[f'{arr_name}'] = f'mat{arr_dim_1}v{arr_dim_2}float'
                self._add_id_dict(self.token.token_str, opname, f'mat{arr_dim_1}v{arr_dim_2}float')
            self.token = self._get_token()  # , or )
        while self.token.token_sym == "COMMA":
            self.token = self._get_token()
            if self.token.token_sym == "INTTK":
                self.token = self._get_token()  # IDENFR
                self._add_int_var_symbol(self.token.token_str)
                self._add_new_opnames(self.token.token_str)
                opname = self._add_spirv_opname(self.token.token_str)
                self._add_id_dict(self.token.token_str, opname, 'int')
                para_tlb[f'{self.token.token_str}'] = f'int'
                self.token = self._get_token()  # , or )
            elif self.token.token_sym == "FLTTK":
                self.token = self._get_token()  # IDENFR
                self._add_flt_var_symbol(self.token.token_str)
                self._add_new_opnames(self.token.token_str)
                opname = self._add_spirv_opname(self.token.token_str)
                self._add_id_dict(self.token.token_str, opname, 'float')
                para_tlb[f'{self.token.token_str}'] = f'float'
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
                self._add_new_opnames(self.token.token_str)
                opname = self._add_spirv_opname(self.token.token_str)
                if (arr_dim_2 == None):
                    para_tlb[f'{arr_name}'] = f'v{arr_dim_1}float'
                    self._add_id_dict(self.token.token_str, opname, f'v{arr_dim_1}float')
                else:
                    para_tlb[f'{arr_name}'] = f'mat{arr_dim_1}v{arr_dim_2}float'
                    self._add_id_dict(self.token.token_str, opname, f'mat{arr_dim_1}v{arr_dim_2}float')
                self.token = self._get_token()  # , or )
        return para_tlb

    # <无返回值函数定义> ::= void <标识符> '('<参数表>')''{'<复合语句>'}'
    def _func_def_no_ret(self):
        self.token = self._get_token()  # IDENFR
        func_name = self.token.token_str
        self._add_void_func_symbol(func_name, "VoidFuncSym", self.subprogram_level_stack[-1])
        self.token = self._get_token()  # (
        self._get_into_new_level()
        self.token = self._get_token()
        para_tlb = self._para_tlb()  # )
        # opname
        func_opname_tail = ''
        func_str_tail = ''
        for key in para_tlb.keys():
            func_opname_tail += (para_tlb[key] + '_')
            func_str_tail += (para_tlb[key] + ';')
        self._add_spirv_list_opname(f'OpName %{func_name}_{func_opname_tail} \"{func_name}({func_str_tail}\"')
#       %float = OpTypeFloat 32
#       %v3float = OpTypeVector %float 3
#       %_ptr_Function_v3float = OpTypePointer Function %v3float
#       %9 = OpTypeFunction %v3float %_ptr_Function_v3float %_ptr_Function_v3float %_ptr_Function_v3float %_ptr_Function_v3float
        tmp = self._get_temp()
        op_type_function = f'{tmp} = OpTypeFunction %void '
        for key in para_tlb.keys():
            op_type_function += f'%_ptr_Function_{para_tlb[key]} '
            # %_ptr_Function_{para_tlb[key]} 补充到 buildin 中吧 
        self._add_spirv_list_define(op_type_function)
        self._add_spirv_list_func(f'%{func_name}_{func_opname_tail} = OpFunction %void None {tmp}')
        # 暂时不考虑重载
        self.func_dict[func_name] = [f'%{func_name}_{func_opname_tail}', '%void', para_tlb]
        # todo: 未考虑参数名重复的情况
        for key in para_tlb.keys():
            self._add_spirv_list_func(f'%{key} = OpFunctionParameter %_ptr_Function_{para_tlb[key]}')
        self._add_spirv_list_func(f'{self._get_temp()} = OpLabel')
        self.func_opvariable_index = len(self.spirv_list_funcs)
        self.token = self._get_token()  # {
        self.token = self._get_token()
        self._compound_statements()  # }
        self._add_spirv_list_func(f'OpFunctionEnd')
        self.token = self._get_token()
        self._exit_cur_level()

    # <声明头部> ::= <类型标识符> <标识符>
    def _declaration_head(self):
        ret_type = ''
        if self.token.token_sym == "INTTK":
            self.token = self._get_token()  # IDENFR
            self._add_int_func_symbol(self.token.token_str)
            ret_type = f'%int'
        elif self.token.token_sym == "FLTTK":
            self.token = self._get_token()  # IDENFR
            self._add_flt_func_symbol(self.token.token_str)
            ret_type = f'%float'
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
            if (arr_dim_2 == None):
                ret_type = f'%v{arr_dim_1}float'
            else:
                ret_type = f'%mat{arr_dim_1}v{arr_dim_2}float'
        func_name = self.token.token_str
        self.token = self._get_token()  # (
        return ret_type, func_name

    # <有返回值函数定义> ::= <声明头部>'('<参数表>')''{'<复合语句>'}'
    def _func_def_with_ret(self):
        ret_type, func_name = self._declaration_head()  # (
        self._get_into_new_level()
        self.token = self._get_token()
        para_tlb = self._para_tlb()  # )
        # opname
        func_opname_tail = ''
        func_str_tail = ''
        for key in para_tlb.keys():
            func_opname_tail += (para_tlb[key] + '_')
            func_str_tail += (para_tlb[key] + ';')
        self._add_spirv_list_opname(f'OpName %{func_name}_{func_opname_tail} \"{func_name}({func_str_tail}\"')
#       %float = OpTypeFloat 32
#       %v3float = OpTypeVector %float 3
#       %_ptr_Function_v3float = OpTypePointer Function %v3float
#       %9 = OpTypeFunction %v3float %_ptr_Function_v3float %_ptr_Function_v3float %_ptr_Function_v3float %_ptr_Function_v3float
        tmp = self._get_temp()
        op_type_function = f'{tmp} = OpTypeFunction {ret_type} '
        for key in para_tlb.keys():
            op_type_function += f'%_ptr_Function_{para_tlb[key]} '
            # %_ptr_Function_{para_tlb[key]} 补充到 buildin 中吧 
        self._add_spirv_list_define(op_type_function)
        self._add_spirv_list_func(f'%{func_name}_{func_opname_tail} = OpFunction {ret_type} None {tmp}')
        # 暂时不考虑重载
        self.func_dict[func_name] = [f'%{func_name}_{func_opname_tail}', ret_type, para_tlb]
        # todo: 未考虑参数名重复的情况
        for key in para_tlb.keys():
            self._add_spirv_list_func(f'%{key} = OpFunctionParameter %_ptr_Function_{para_tlb[key]}')
        self._add_spirv_list_func(f'{self._get_temp()} = OpLabel')
        self.func_opvariable_index = len(self.spirv_list_funcs)
        self.token = self._get_token()  # {
        self.token = self._get_token()
        self._compound_statements()  # }
        self._add_spirv_list_func(f'OpFunctionEnd')
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
            name, _ = self._get_id_info(self.token.token_str)
            self._assign_statement(name)
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
        func_name = self.token.token_str
        func_info = self.func_dict[func_name]
        param_names = []
        for key in func_info[2]:
            self._add_new_opnames('param')
            param_name = self._add_spirv_opname('param')
            param_names.append(param_name)
            self._add_spirv_list_func(f'{param_name} = OpVariable %_ptr_Function_{func_info[2][key]} Function')
        self.token = self._get_token()  # (
        self.token = self._get_token()  # ) or IDENFR
        param_values = self._value_para_tlb()  # )
        # 给param赋值
        for i in range(len(param_names)):
            self._add_spirv_list_func(f'OpStore {param_names[i]} {param_values[i]}')
        # 调用
        tmp = self._get_temp()
        call_func_spv = f'{tmp} = OpFunctionCall {func_info[1]} {func_info[0]} '
        for i in param_names:
            call_func_spv += f'{i} '
        self._add_spirv_list_func(call_func_spv)
        self.token = self._get_token()  # ;
        return (tmp, func_info[1])

    # <无返回值函数调用语句> ::= <标识符>'('<值参数表>')'
    def _func_call_no_ret(self):
        func_name = self.token.token_str
        self.token = self._get_token()  # (
        self.token = self._get_token()  # ) or IDENFR
        self._value_para_tlb()  # )
        self.token = self._get_token()  # ;

    # <值参数表> ::= <表达式>{, <表达式>} | <空>
    def _value_para_tlb(self):
        tmps = []
        if self._is_expr():
            tmps.append(self._expr()[0])
            while self.token.token_sym == "COMMA":
                self.token = self._get_token()
                tmps.append(self._expr()[0])
        return tmps

    # <返回语句> ::= return [<表达式>]
    def _ret_statement(self):
        self.token = self._get_token()
        if self.token.token_sym != "SEMICN":
            tmp, _ = self._expr()
            self._add_spirv_list_func(f'OpReturnValue {tmp}')

    '''
    <赋值语句> ::= <标识符> = <表达式>b
        | <标识符> = '{'<表达式>{, <表达式>}'}' 
        | <标识符> = '{''{'<表达式>{, <表达式>}'}'{, '{'<表达式>{, <表达式>}'}'}'}'
        | <标识符>'['<表达式>']' = <表达式>
        | <标识符>'['<表达式>']''['<表达式>']' = <表达式> 
    '''
    def _assign_statement(self, name):
        tmp = ''
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
                    tmps2 = []
                    for _ in range(symbol.arr_dim_2):
                        tmps2.append(self._expr()[0])  # , or }
                        self.token = self._get_token()
                    tmp = self._get_temp()
                    tmps2_str = ''
                    for t in tmps2:
                        tmps2_str += (t + ' ')
                    self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct %v{len(tmps2)}float {tmps2_str}')
                    tmps1 = [tmp]
                    for _ in range(symbol.arr_dim_1 - 1):
                        self.token = self._get_token()  # {
                        self.token = self._get_token()
                        tmps2 = []
                        for _ in range(symbol.arr_dim_2):
                            tmps2.append(self._expr()[0])  # , or }
                            self.token = self._get_token()
                        tmp = self._get_temp()
                        tmps2_str = ''
                        for t in tmps2:
                            tmps2_str += (t + ' ')
                        self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct %v{len(tmps2)}float {tmps2_str}')
                        tmps1.append(tmp)
                    tmps1_str = ''
                    for t in tmps1:
                        tmps1_str += (t + ' ')
                    tmp = self._get_temp()
                    self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct %mat{symbol.arr_dim_1}v{symbol.arr_dim_2}float {tmps1_str}')
                    self._add_spirv_list_func(f'OpStore {name} {tmp}')
                    self.token = self._get_token()  # ;
                else:
                    # <标识符> = '{'<表达式>{, <表达式>}'}';
                    self.token = self._get_token()
                    tmps = []
                    for _ in range(symbol.arr_dim_1):
                        tmps.append(self._expr()[0])  # , or }
                        self.token = self._get_token()
                    tmp = self._get_temp()
                    tmps_str = ''
                    for t in tmps:
                        tmps_str += (t + ' ')
                    self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct %v{len(tmps)}float {tmps_str}')
                    self._add_spirv_list_func(f'OpStore {name} {tmp}')
            else:
                tmp, _ = self._expr()  # ;
                self._add_spirv_list_func(f'OpStore {name} {tmp}')
        else:
            # todo: 给列表中的某个元素赋值
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
        (tmp, tmp_type) = (term_tmp, term_tmp_type) = self._term()
        if is_first_sym_minu:
            tmp = self._get_temp()
            if term_tmp_type == f'%float':
                self._add_spirv_list_func(f'{tmp} = OpFMul %float %float_n1 {term_tmp}')
            else:
                self._add_spirv_list_func(f'{tmp} = OpVectorTimesScalar {term_tmp_type} {term_tmp} %float_n1')
        while self.token.token_sym == "PLUS" or self.token.token_sym == "MINU":
            sy = self.token.token_sym
            self.token = self._get_token()
            term_tmp0, term_tmp_type0 = tmp, tmp_type
            term_tmp1, term_tmp_type1 = self._term()
            tmp = self._get_temp()
            if term_tmp_type0 == term_tmp_type1 or (term_tmp_type0 == f'%int' and term_tmp_type1 == f'%float') or (term_tmp_type0 == f'%float' and term_tmp_type1 == f'%int'):
                if sy == "MINU":
                    self._add_spirv_list_func(f'{tmp} = OpFSub {term_tmp_type1} {term_tmp0} {term_tmp1}')
                elif sy == "PLUS":
                    self._add_spirv_list_func(f'{tmp} = OpFAdd {term_tmp_type1} {term_tmp0} {term_tmp1}')
                tmp_type = term_tmp_type1
            else:
                if term_tmp_type0 == f'%float':
                    n = int(term_tmp_type1[2])
                    self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct {term_tmp_type1} ' + n * f'{term_tmp0} ')
                    tmp0 = tmp
                    tmp = self._get_temp()
                    if sy == "MINU":
                        self._add_spirv_list_func(f'{tmp} = OpFSub {term_tmp_type1} {tmp0} {term_tmp1}')
                    elif sy == "PLUS":
                        self._add_spirv_list_func(f'{tmp} = OpFAdd {term_tmp_type1} {tmp0} {term_tmp1}')
                    tmp_type = term_tmp_type1
                elif term_tmp_type1 == f'%float':
                    n = int(term_tmp_type0[2])
                    self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct {term_tmp_type0} ' + n * f'{term_tmp1} ')
                    tmp1 = tmp
                    tmp = self._get_temp()
                    if sy == "MINU":
                        self._add_spirv_list_func(f'{tmp} = OpFSub {term_tmp_type0} {term_tmp0} {tmp1}')
                    elif sy == "PLUS":
                        self._add_spirv_list_func(f'{tmp} = OpFAdd {term_tmp_type0} {term_tmp0} {tmp1}')
                    tmp_type = term_tmp_type0
        return tmp, tmp_type


    # <项> ::= <因子>{<乘法运算符><因子>}
    def _term(self):
        tmp, tmp_type = self._factor()
        while self.token.token_sym == "MULT" or self.token.token_sym == "DIV":
            sy = self.token.token_sym
            self.token = self._get_token()
            term_tmp0, term_tmp_type0 = tmp, tmp_type
            term_tmp1, term_tmp_type1 = self._factor()
            tmp = self._get_temp()
            if term_tmp_type0 == term_tmp_type1 or (term_tmp_type0 == f'%int' and term_tmp_type1 == f'%float') or (term_tmp_type0 == f'%float' and term_tmp_type1 == f'%int'):
                if sy == "MULT":
                    self._add_spirv_list_func(f'{tmp} = OpFMul {term_tmp_type1} {term_tmp0} {term_tmp1}')
                elif sy == "DIV":
                    self._add_spirv_list_func(f'{tmp} = OpFDiv {term_tmp_type1} {term_tmp0} {term_tmp1}')
                tmp_type = term_tmp_type1
            else:
                if term_tmp_type0 == f'%float':
                    if sy == "MULT":
                        self._add_spirv_list_func(f'{tmp} = OpVectorTimesScalar {term_tmp_type1} {term_tmp1} {term_tmp0}')
                    elif sy == "DIV":
                        pass
                        # tmp = self._get_temp()
                        # self._add_spirv_list_func(f'{tmp} = OpCompositeConstruct {term_tmp_type1} {term_tmp0} {term_tmp1}')
                        # self._add_spirv_list_func(f'{tmp} = OpFDiv {term_tmp_type1} {term_tmp0} {term_tmp1}')
                    tmp_type = term_tmp_type1
                elif term_tmp_type1 == f'%float':
                    if sy == "MULT":
                        self._add_spirv_list_func(f'{tmp} = OpVectorTimesScalar {term_tmp_type0} {term_tmp0} {term_tmp1}')
                    elif sy == "DIV":
                        pass
                    tmp_type = term_tmp_type0
        return (tmp, tmp_type)

    '''
    <因子> ::= <标识符> | <标识符>'['<表达式>']' | <标识符>'['<表达式']''['<表达式']'
        | '('<表达式>')' | <整数> | <小数> | <有返回值函数调用语句>
    '''
    def _factor(self):
        tmp = ''
        tmp_type = ''
        if self._is_func_call():
            # <有返回值函数调用语句>
            func_name = self.token.token_str.lower()
            tmp, tmp_type = self._func_call_with_ret()
        elif self.token.token_sym == "IDENFR":
            symbol_name = self.token.token_str
            symbol = self._get_symbol_latest(symbol_name)
            self.token = self._get_token()
            dim1 = None
            dim2 = None
            if self.token.token_sym == "LBRACK":
                self.token = self._get_token()
                dim1, _ = self._expr()  # ]
                self.token = self._get_token()
                if self.token.token_sym == "LBRACK":
                    self.token = self._get_token()
                    # dim2 = self._expr()
                    self._expr()
                    self.token = self._get_token()
            tmp = self._get_temp()
            if not dim1 and not dim2:
                tmp_type = f'%{self._get_id_info(symbol_name)[1]}'
                self._add_spirv_list_func(f'{tmp} = OpLoad %{self._get_id_info(symbol_name)[1]} {self._get_id_info(symbol_name)[0]}')
            elif dim1 and not dim2:
                if symbol_name in self.build_in_vars:
                    self._add_spirv_list_func(f'{tmp} = OpAccessChain %_ptr_Private_float %{symbol_name} {dim1}')
                else:
                    self._add_spirv_list_func(f'{tmp} = OpAccessChain %_ptr_Function_float %{symbol_name} {dim1}')
                tmp0 = tmp
                tmp = self._get_temp()
                self._add_spirv_list_func(f'{tmp} = OpLoad %float {tmp0}')
                tmp_type = f'%float'
            else:
                pass
        elif self.token.token_sym == "LPARENT":
            self.token = self._get_token()
            tmp, tmp_type = self._expr()  # )
            self.token = self._get_token()
        elif self.token.token_sym == "PLUS" or self.token.token_sym == "MINU" or \
            self.token.token_sym == "INTCON" or self.token.token_sym == "FLTCON":
            const_value = self._const_sym()
            if self.token.token_sym == "INTCON":
                if const_value >= 0:
                    tmp = f'%int_{int(const_value)}'
                else:
                    tmp = f'%int_n{-int(const_value)}'
                if not self._find_defined_type(tmp):
                    self._add_spirv_list_define(f'{tmp} = OpConstant %int {int(const_value)}')
                tmp_type = f'%int'
            elif self.token.token_sym == "FLTCON":
                if const_value >= 0:
                    tmp = f'%float_{int(const_value)}_{str(const_value-int(const_value))[2:]}'
                else:
                    tmp = f'%float_n{int(-const_value)}_{str(-const_value-int(-const_value))[2:]}'
                if not self._find_defined_type(tmp):
                    self._add_spirv_list_define(f'{tmp} = OpConstant %float {const_value}')
                tmp_type = f'%float'
            self.token = self._get_token()
        return (tmp, tmp_type)

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

    def to_spvasm(self, file):
        asm = self.build_in_templates[0:22]
        asm.extend(self.spirv_list_opnames)
        asm.extend(self.build_in_templates[22:151])
        asm.extend(self.spirv_list_defines)
        asm.extend(self.build_in_templates[151:])
        asm.extend(self.spirv_list_funcs)
        with open('main.frag.esl.spvasm', mode='w', encoding='utf-8') as f:
            f.writelines(asm)
        f.close()

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
        # self._main_func()
        self._exit_cur_level()
        print(self.token, self.token.token_sym, self.token.token_str, self.token.line)
        # print(self.func_dict)
        # print(self.spirv_list_opnames)
        # print(self.spirv_list_funcs)
        # print(self.spirv_list_defines)
        self.to_spvasm('')

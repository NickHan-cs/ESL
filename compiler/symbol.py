class Symbol(object):

    def __init__(self, name, type, level):
        self.name = name
        self.type = type
        self.level = level


class IntVarSymbol(Symbol):

    def __init__(self, name, type, level):
        super().__init__(name, type, level)


class FltVarSymbol(Symbol):

    def __init__(self, name, type, level):
        super().__init__(name, type, level)


class ArrVarSymbol(Symbol):

    def __init__(self, name, type, level, arr_dim_1, arr_dim_2, in_out_type=None):
        super().__init__(name, type, level)
        self.arr_dim_1 = arr_dim_1
        self.arr_dim_2 = arr_dim_2
        self.in_out_type = in_out_type


class VoidFuncSymbol(Symbol):

    def __init__(self, name, type, level):
        super().__init__(name, type, level)


class IntFuncSymbol(Symbol):

    def __init__(self, name, type, level):
        super().__init__(name, type, level)


class FltFuncSymbol(Symbol):

    def __init__(self, name, type, level):
        super().__init__(name, type, level)


class ArrFuncSymbol(Symbol):

    def __init__(self, name, type, level, arr_dim_1, arr_dim_2):
        super().__init__(name, type, level)
        self.arr_dim_1 = arr_dim_1
        self.arr_dim_2 = arr_dim_2


class BuiltInFuncSymbol(Symbol):

    def __init__(self, name, type, level):
        super().__init__(name, type, level)

class Spriv(object):

    def __init__(self, op_name, is_assign, args) -> None:
        self.op_name = op_name
        self.is_assign = is_assign
        self.args = args
    
    def __str__(self) -> str:
        re = f'{self.op_name}'
        if (self.is_assign):
            re = f'{self.args[0]} = ' + re
            for i in range(1, len(self.args)):
                re += f' {self.args[i]}'
        else:
            for i in range(0, len(self.args)):
                re += f' {self.args[i]}'
        return re

ops = { 
        'op_name': 'OpName', 
        'op_type_void': 'OpTypeVoid',
        'op_type_int': 'OpTypeInt', 
        'op_type_bool': 'OpTypeBool',
        'op_type_float': 'OpTypeFloat',
        'op_type_vector': 'OpTypeVector',
        'op_type_array': 'OpTypeArray',
        'op_type_struct': 'OpTypeStruct',
        'op_type_pointer': 'OpTypePointer',
        'op_type_function': 'OpTypeFunction',
        'op_label': 'OpLabel',
        'op_constant': 'OpConstant',
        'op_constant_composite': 'OpConstantComposite',
        'op_variable': 'OpVariable',
        'op_access_chain': 'OpAccessChain',
        'op_composite_extract': 'OpCompositeExtract',
        'op_load': 'OpLoad',
        'op_store': 'OpStore',
        'op_imul': 'OpIMul',
        'op_isub': 'OpISub',
        'op_sdiv': 'OpSDiv',
        'op_fsub': 'OpFSub',
        'op_selection_merge': 'OpSelectionMerge',
        'op_branch': 'OpBranch',
        'op_branch_conditional': 'OpBranchConditional',
        'op_vector_shuffle': 'OpVectorShuffle',
        'op_ext_inst': 'OpExtInst',
        'op_function_call': 'OpFunctionCall',
        'op_function': 'OpFunction',
        'op_function_parameter': 'OpFunctionParameter',
        'op_return': 'OpReturn',
        'op_return_value': 'OpReturnValue',
        'op_function_end': 'OpFunctionEnd',
        'op_inot_equal': 'OpINotEqual',
        'op_ford_greater_than_equal': 'OpFOrdGreaterThanEqual',
        'op_ford_less_than_equal': 'OpFOrdLessThanEqual',
        'op_phi': 'OpPhi',
        'op_select': 'OpSelect',
        'op_vector_time_scalar': 'OpVectorTimesScalar'
      }
import re
import solcx

def remove_swarm_hash(bytecode):
    if isinstance(bytecode, str):
        if bytecode.endswith('0029'):
            bytecode = re.sub(r'a165627a7a72305820\S{64}0029$', '', bytecode)
        if bytecode.endswith('0033'):
            bytecode = re.sub(r'5056fe.*?0033$', '5056', bytecode)
    return bytecode

def convert_stack_value_to_int(stack_value):
    if stack_value[0] == int:
        return stack_value[1]
    elif stack_value[0] == bytes:
        return int.from_bytes(stack_value[1], 'big')
    else:
        print('Error: Cannot convert stack value to int. Unknown type --> ' + str(stack_value[0]))

def compile(solc_version, evm_version, source_code_file):
    compiler_res = None
    source_code = ''
    with open(source_code_file, 'r') as file:
        source_code = file.read()
    try:
        solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version, True)
        compiler_res = solcx.compile_standard({
            'language': 'Solidity',
            'sources': { source_code_file: { 'content': source_code } },
            'settings': {
                'optimizer': {
                    'enabled': True,
                    'runs': 200
                },
                'evmVersion': evm_version,
                'outputSelection': {
                    source_code_file: {
                        '*': [ 'evm.deployedBytecode' ]   
                    }
                }
            }
        }, allow_paths='.')
    except Exception as e:
        print('Error: Solidity compilation failed! --> ', e)
        
    return compiler_res
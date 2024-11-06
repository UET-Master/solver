from utils import remove_swarm_hash, convert_stack_value_to_int
import eth

# The block contains instructions and it is actually a vertex in CFG
class Block:
    def __init__(self):
        self.start_address = None
        self.end_address = None
        self.instructions = dict()

    def set_start_address(self, start_address):
        self.start_address = start_address

    def get_start_address(self):
        return self.start_address

    def set_end_address(self, end_address):
        self.end_address = end_address

    def get_end_address(self):
        return self.end_address

    def add_instruction(self, key, value):
        self.instructions[key] = value

    def get_instructions(self):
        return self.instructions

class ControlFlowGraph:
    def __init__(self):
        self.edges = dict()
        self.vertices = dict()
        self.visited_pcs = set()
        self.visited_branches = dict()
        self.error_pcs = set()

    def build(self, bytecode):
        bytecode = bytes.fromhex(bytecode)
        current_pc = 0
        previous_pc = 0
        block = None
        previous_opcode = None
        previous_push_value = str()
        while current_pc < len(bytecode):
            opcode = bytecode[current_pc]

            if previous_opcode == 255: # SELFDESTRUCT
                block.set_end_address(previous_pc)
                self.vertices[current_pc] = block
                block = None

            if block is None:
                block = Block()
                block.set_start_address(current_pc)

            if opcode == 91 and block.get_instructions(): # JUMPDEST
                block.set_end_address(previous_pc)
                if previous_pc not in self.edges and previous_opcode not in [0, 86, 87, 243, 253, 254, 255]: # Termination and condition
                    self.edges[previous_pc] = []
                    self.edges[previous_pc].append(current_pc)
                self.vertices[current_pc] = block
                block = Block()
                block.set_start_address(current_pc)

            if opcode < 96 or opcode > 127: # PUSH??
                if opcode in self.opcode_to_mnemonic:
                    block.add_instruction(current_pc, self.opcode_to_mnemonic[opcode])
                else:
                    block.add_instruction(current_pc, 'Missing opcode ' + hex(opcode))

            if opcode == 86 or opcode == 87: # JUMP or JUMPI
                block.set_end_address(current_pc)
                self.vertices[current_pc] = block
                block = None
                if opcode == 86 and previous_opcode and previous_opcode >= 96 and previous_opcode <= 127: # JUMP
                    if current_pc not in self.edges:
                        self.edges[current_pc] = []
                    self.edges[current_pc].append(previous_push_value)
                if opcode == 87: # JUMPI
                    if current_pc not in self.edges:
                        self.edges[current_pc] = []
                    self.edges[current_pc].append(current_pc+1)
                    if previous_opcode and previous_opcode >= 96 and previous_opcode <= 127:
                        if current_pc not in self.edges:
                            self.edges[current_pc] = []
                        self.edges[current_pc].append(previous_push_value)

            previous_pc = current_pc
            if opcode >= 96 and opcode <= 127: # PUSH??
                size = opcode - 96 + 1
                for i in range(size):
                    try:
                        previous_push_value += str(hex(bytecode[current_pc + i + 1])).replace('0x', '').zfill(2)
                    except Exception as e:
                        print('Error: Problem with creating a new string --> ', e)
                if previous_push_value:
                    previous_push_value = '0x' + previous_push_value
                    block.add_instruction(current_pc, self.opcode_to_mnemonic[opcode] + ' ' + previous_push_value)
                    previous_push_value = int(previous_push_value, 16)
                    current_pc += size

            current_pc += 1
            previous_opcode = opcode

        if block:
            block.set_end_address(previous_pc)
            self.vertices[current_pc] = block

    def save_control_flow_graph(self, filename):
        f = open(filename+'.dot', 'w')
        f.write('digraph cfg {\n')
        f.write('rankdir = TB;\n')
        f.write('size = "240"\n')
        f.write('graph[fontname = Courier, fontsize = 14.0, labeljust = l, nojustify = true];node[shape = record];\n')
        address_width = 10
        
        for block in self.vertices.values():
            if len(hex(list(block.get_instructions().keys())[-1])) > address_width:
                address_width = len(hex(list(block.get_instructions().keys())[-1]))
        
        for block in self.vertices.values():
            # Draw vertices
            label = '"' + hex(block.get_start_address()) + '"[label="'
            for address in block.get_instructions():
                label += '{0:#0{1}x}'.format(address, address_width) + ' ' + block.get_instructions()[address] + '\l'
            visited_block = False
            for pc in self.error_pcs:
                if pc in block.get_instructions().keys():
                    f.write(label + '",style=filled,fillcolor=red];\n')
                    visited_block = True
                    break
            if not visited_block:
                if  block.get_start_address() in self.visited_pcs and block.get_end_address() in self.visited_pcs:
                    f.write(label + '",style=filled,fillcolor=gray];\n')
                else:
                    f.write(label + '",style=filled,fillcolor=white];\n')
            # Draw edges
            if block.get_end_address() in self.edges:
                # JUMPI
                if list(block.get_instructions().values())[-1] == "JUMPI":
                    if hex(block.get_end_address()) in self.visited_branches and 0 in self.visited_branches[hex(block.get_end_address())] and self.visited_branches[hex(block.get_end_address())][0]["expression"]:
                        f.write('"'+ hex(block.get_start_address()) +'" -> "'+ hex(self.edges[block.get_end_address()][0]) +'" [label=" '+ str(self.visited_branches[hex(block.get_end_address())][0]["expression"][-1]) +'",color="red"];\n')
                    else:
                        f.write('"'+ hex(block.get_start_address()) +'" -> "'+ hex(self.edges[block.get_end_address()][0]) +'" [label="",color="red"];\n')
                    if hex(block.get_end_address()) in self.visited_branches and 1 in self.visited_branches[hex(block.get_end_address())] and self.visited_branches[hex(block.get_end_address())][1]["expression"]:
                        f.write('"'+ hex(block.get_start_address())+'" -> "'+ hex(self.edges[block.get_end_address()][1]) +'" [label=" '+str(self.visited_branches[hex(block.get_end_address())][1]["expression"][-1]) +'",color="green"];\n')
                    else:
                        f.write('"'+ hex(block.get_start_address())+'" -> "'+ hex(self.edges[block.get_end_address()][1]) +'" [label="",color="green"];\n')
                # Other instructions
                else:
                    for i in range(len(self.edges[block.get_end_address()])):
                        f.write('"'+ hex(block.get_start_address()) +'" -> "'+ hex(self.edges[block.get_end_address()][i]) +'" [label="",color="black"];\n')
        f.write('}\n')
        f.close()

    # Using the EVM version - Shanghai
    opcode_to_mnemonic = {
        # 0s: Stop and Arithmetic Operations
        0: 'STOP',
        1: 'ADD',
        2: 'MUL',
        3: 'SUB',
        4: 'DIV',
        5: 'SDIV',
        6: 'MOD',
        7: 'SMOD',
        8: 'ADDMOD',
        9: 'MULMOD',
        10: 'EXP',
        11: 'SIGNEXTEND',
        # 10s: Comparison & Bitwise Logic Operations
        16: 'LT',
        17: 'GT',
        18: 'SLT',
        19: 'SGT',
        20: 'EQ',
        21: 'ISZERO',
        22: 'AND',
        23: 'OR',
        24: 'XOR',
        25: 'NOT',
        26: 'BYTE',
        27: 'SHL',
        28: 'SHR',
        29: 'SAR',
        # 20s: KECCAK256
        32: 'KECCAK256',
        # 30s: Environmental Information
        48: 'ADDRESS',
        49: 'BALANCE',
        50: 'ORIGIN',
        51: 'CALLER',
        52: 'CALLVALUE',
        53: 'CALLDATALOAD',
        54: 'CALLDATASIZE',
        55: 'CALLDATACOPY',
        56: 'CODESIZE',
        57: 'CODECOPY',
        58: 'GASPRICE',
        59: 'EXTCODESIZE',
        60: 'EXTCODECOPY',
        61: 'RETURNDATASIZE',
        62: 'RETURNDATACOPY',
        63: 'EXTCODEHASH',
        # 40s: Block Information
        64: 'BLOCKHASH',
        65: 'COINBASE',
        66: 'TIMESTAMP',
        67: 'NUMBER',
        68: 'PREVRANDAO',
        69: 'GASLIMIT',
        70: 'CHAINID',
        71: 'SELFBALANCE',
        72: 'BASEFEE',
        # 50s: Stack, Memory, Storage and Flow Operations
        80: 'POP',
        81: 'MLOAD',
        82: 'MSTORE',
        83: 'MSTORE8',
        84: 'SLOAD',
        85: 'SSTORE',
        86: 'JUMP',
        87: 'JUMPI',
        88: 'PC',
        89: 'MSIZE',
        90: 'GAS',
        91: 'JUMPDEST',
        # 5f, 60s & 70s: Push Operations
        95: "PUSH0",
        96: 'PUSH1',
        97: 'PUSH2',
        98: 'PUSH3',
        99: 'PUSH4',
        100: 'PUSH5',
        101: 'PUSH6',
        102: 'PUSH7',
        103: 'PUSH8',
        104: 'PUSH9',
        105: 'PUSH10',
        106: 'PUSH11',
        107: 'PUSH12',
        108: 'PUSH13',
        109: 'PUSH14',
        110: 'PUSH15',
        111: 'PUSH16',
        112: 'PUSH17',
        113: 'PUSH18',
        114: 'PUSH19',
        115: 'PUSH20',
        116: 'PUSH21',
        117: 'PUSH22',
        118: 'PUSH23',
        119: 'PUSH24',
        120: 'PUSH25',
        121: 'PUSH26',
        122: 'PUSH27',
        123: 'PUSH28',
        124: 'PUSH29',
        125: 'PUSH30',
        126: 'PUSH31',
        127: 'PUSH32',
        # 80s: Duplication Operations
        128: 'DUP1',
        129: 'DUP2',
        130: 'DUP3',
        131: 'DUP4',
        132: 'DUP5',
        133: 'DUP6',
        134: 'DUP7',
        135: 'DUP8',
        136: 'DUP9',
        137: 'DUP10',
        138: 'DUP11',
        139: 'DUP12',
        140: 'DUP13',
        141: 'DUP14',
        142: 'DUP15',
        143: 'DUP16',
        # 90s: Exchange Operations
        144: 'SWAP1',
        145: 'SWAP2',
        146: 'SWAP3',
        147: 'SWAP4',
        148: 'SWAP5',
        149: 'SWAP6',
        150: 'SWAP7',
        151: 'SWAP8',
        152: 'SWAP9',
        153: 'SWAP10',
        154: 'SWAP11',
        155: 'SWAP12',
        156: 'SWAP13',
        157: 'SWAP14',
        158: 'SWAP15',
        159: 'SWAP16',
        # a0s: Logging Operations
        160: 'LOG0',
        161: 'LOG1',
        162: 'LOG2',
        163: 'LOG3',
        164: 'LOG4',
        # f0s: System Operations
        240: 'CREATE',
        241: 'CALL',
        242: 'CALLCODE',
        243: 'RETURN',
        244: 'DELEGATECALL',
        245: 'CREATE2',
        250: 'STATICCALL',
        253: 'REVERT',
        254: 'INVALID',
        255: 'SELFDESTRUCT'
    }


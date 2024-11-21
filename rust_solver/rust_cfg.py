import re
from utils import clean_instructions

class Block:
    def __init__(self):
        self.block_address = None
        self.instructions = list()

    def set_block_address(self, address):
        self.block_address = address

    def get_block_address(self):
        return self.block_address
    
    def add_instruction(self, value):
        self.instructions.append(value)

    def get_instructions(self):
        return self.instructions

class ControlFlowGraph:
    # The mnemonic represents the instructions for jumping from block A1 to block A2
    jump_mnemonic = { 
        0: 'goto', 
        1: 'return', 
        2: 'success',
        3: '0',
        4: '1'
    }
    # The mnemonic represents the instructions terminating the program
    termination_mnemonic = { 'unreachable', 'return' }

    def __init__(self):
        self.edges = dict()
        self.vertices = dict()
        self.paths = dict()
        self.visited_paths = dict()
        self.visited_branches = dict()

    def build(self, mir_codes, considered_func = 'addition'):
        # The checkpoint indicates the following code are considered
        scope_checkpoint = False
        # The checkpoint indicates the following block are considered
        block_checkpoint = False
        block_id = None
        block = None

        for code in mir_codes:
            code = str(code)
            if code.startswith('fn') and not considered_func in code:
                break

            if code.startswith('fn') and considered_func in code:
                scope_checkpoint = True

            if scope_checkpoint == True:
                if block is None:
                    block = Block()

                if code.startswith('bb'):
                    block_checkpoint = True
                    block_id = code[code.find('bb'):code.find(':')]
                    if any(termination_code in code for termination_code in self.termination_mnemonic):
                        found_instruction = next(termination_code for termination_code in self.termination_mnemonic if termination_code in code)
                        block.add_instruction(found_instruction)
                        self.vertices[block_id] = found_instruction
                        block = None
                
                if re.match(r"^_\d+", code) and re.search(r"\[.*?\]", code) is None and block_checkpoint: 
                    block.add_instruction(code)

                if re.search(r"\[.*?\]", code) and block_checkpoint:
                    # An example of code: switchInt(move _8) -> [0: bb6, 1: bb5, otherwise: bb4]
                    extractions = code.split(' -> ')
                    block.add_instruction(extractions[0])
                    
                    self.edges[block_id] = []
                    true_path_indicator = self.jump_mnemonic[4] + ':'
                    false_path_indicator = self.jump_mnemonic[3] + ':'
                    if true_path_indicator in extractions[1] or false_path_indicator in extractions[1]:
                        self.visited_branches[block_id] = dict()

                    jump_conditions = extractions[1].split(',')
                    for condition in jump_conditions:
                        if self.jump_mnemonic[1] in condition or self.jump_mnemonic[2] in condition: # return or success
                            self.edges[block_id].append(condition.split(':')[1].strip())

                        if false_path_indicator in condition: #  0 (False)
                            self.edges[block_id].append(condition.split(':')[1].strip())
                            self.visited_branches[block_id][0] = { 'expression': extractions[0] + ' == ' + self.jump_mnemonic[3] }
                        
                        if true_path_indicator in condition: #  1 (True)
                            self.edges[block_id].append(condition.split(':')[1].strip())
                            self.visited_branches[block_id][1] = { 'expression': extractions[0] + ' == ' + self.jump_mnemonic[4] }
                
                if self.jump_mnemonic[0] in code and block_checkpoint:
                    self.edges[block_id] = []
                    self.edges[block_id].append(code[code.find('bb'):code.find(':')])

                # Mark the end of a block
                if code.startswith('}') and block_checkpoint:
                    self.vertices[block_id] = block
                    block_checkpoint = False
                    block_id = None
                    block = None

    def save_control_flow_graph(self, cfg_file):
        f = open(cfg_file, 'w')
        f.write('digraph cfg {\n')
        f.write('rankdir = TB;\n')
        f.write('size = "240"\n')
        f.write('graph[fontname = Courier, fontsize = 14.0, labeljust = l, nojustify = true];node[shape = record];\n')
        
        for block_id, block in self.vertices.items():
            print("Block ---> ", block_id, block.get_instructions())
            # Draw vertices
            label = '"' + block_id + '"[label="'
            if len(block.get_instructions()) == 0:
                continue
            for instruction in block.get_instructions():
                label += clean_instructions(instruction) + '\l'
            f.write(label + '",style=filled,fillcolor=white];\n')

            # Draw edges
            if block_id in self.edges:
                if block_id in self.visited_branches and 0 in self.visited_branches[block_id]:
                    f.write('"' + block_id + '" -> "' + self.edges[block_id][0] + '" [label="' + self.visited_branches[block_id][0]['expression'] + '",color="red"];\n') 
                 
                if block_id in self.visited_branches and 1 in self.visited_branches[block_id]:
                    f.write('"' + block_id + '" -> "' + self.edges[block_id][1] + '" [label="' + self.visited_branches[block_id][1]['expression'] + '",color="green"];\n') 
                
                if block_id not in self.visited_branches:
                    for adjacent_block_id in self.edges[block_id]:
                        f.write('"' + block_id + '" -> "' + adjacent_block_id + '" [label="",color="black"];\n')

        f.write('}\n')
        f.close()

                
        


import re

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
        current_block = None
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
                    current_block = code[code.find('bb'):code.find(':')]
                    if any(termination_code in code for termination_code in self.termination_mnemonic):
                        found_instruction = next(termination_code for termination_code in self.termination_mnemonic if termination_code in code)
                        block = Block()
                        block.add_instruction(found_instruction)
                        self.vertices[current_block] = found_instruction
                        block = None
                
                if re.match(r"^_\d+", code) and re.match(r"\[.*?\]", code) is None and block_checkpoint: 
                    block.add_instruction(code)

                if re.match(r"\[.*?\]", code):
                    extractions = code.split('->')
                    block.add_instruction(extractions[0])
                    # An example for extractions[1] is [0: bb6, 1: bb5, otherwise: bb4]
                    jump_conditions = extractions[1].split(',')
                    self.edges[current_block] = []
                    self.visited_branches[current_block] = []
                    for condition in jump_conditions:
                        if self.jump_mnemonic[1] in condition or self.jump_mnemonic[2] in condition: # return or success
                            self.edges[current_block].append(condition.split(':')[1].strip())

                        if self.jump_mnemonic[3] in condition: #  0 (False)
                            self.edges[current_block].append(condition.split(':')[1].strip())
                            self.visited_branches[current_block][0]['expression'] = extractions[0] + ' == ' + self.jump_mnemonic[3]

                        if self.jump_mnemonic[4] in condition: #  1 (True)
                            self.edges[current_block].append(condition.split(':')[1].strip())
                            self.visited_branches[current_block][1]['expression'] = extractions[0] + ' == ' + self.jump_mnemonic[4]
                
                if self.jump_mnemonic[0] in code and block_checkpoint:
                    self.edges[current_block].append(code.split('->')[1])

                if code.startswith('}') and block_checkpoint:
                    self.vertices[current_block] = block
                    block_checkpoint = False
                    current_block = None

    def save_control_flow_graph(self, cfg_file):
        f = open(cfg_file, 'w')
        f.write('digraph cfg {\n')
        f.write('rankdir = TB;\n')
        f.write('size = "240"\n')
        f.write('graph[fontname = Courier, fontsize = 14.0, labeljust = l, nojustify = true];node[shape = record];\n')

        for block_id, block in self.vertices.items():
            # Draw vertices
            label = '"' + block_id + '"[label="'
            for instruction in block.get_instructions():
                label += instruction + '\l'
            f.write('",style=filled,fillcolor=white];\n')

            # Draw edges
            if block_id in self.edges:
                if block_id in self.visited_branches and 0 in self.visited_branches[block_id]:
                    f.write('"' + block_id + '" -> "' + self.edges[block_id][0] + ' "[label="' + self.visited_branches[block_id][0]['expression'] + '",color="red"];\n') 
                elif block_id in self.visited_branches and 1 in self.visited_branches[block_id]:
                    f.write('"' + block_id + '" -> "' + self.edges[block_id][0] + ' "[label="' + self.visited_branches[block_id][0]['expression'] + '",color="green"];\n') 
                else:
                    for adjacent_block_id in self.edges[block_id]:
                        f.write('"' + block_id + '" -> "' + adjacent_block_id + '" [label="",color="black"];\n')

        f.write('}\n')
        f.close()

                
        


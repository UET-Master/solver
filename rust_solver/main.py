import subprocess
from control_flow_graph import ControlFlowGraph

# The solver generates CFG in .dot file and Z3 constraints from the CFG's paths
class Solver:
    def __init__(self, mir_codes):
        rust_cfg = ControlFlowGraph()
        rust_cfg.build(mir_codes)

        self.rust_cfg = rust_cfg

    def run(self, cfg_file):
        self.rust_cfg.save_control_flow_graph(cfg_file)

def main():
    source = 'example/src/main.rs'
    compiler_output_file = 'example/main.mir'
    cfg_file = 'example/main.dot'

    try:
        subprocess.run(['rustc', '--emit=mir', source, '-o', compiler_output_file], check=True, text=True)
    except Exception as e:
        print('Error in getting MIR --> ', e)

    mir_codes = list()
    with open(compiler_output_file, mode='r') as file:
        file_lines = file.readlines()
        mir_codes = [line.strip() for line in file_lines]
    solver = Solver(mir_codes)
    solver.run(cfg_file)

if '__main__' == __name__:
    main()
import os
import sys
from utils import compile
from control_flow_graph import ControlFlowGraph


# The solver generates CFG in .dot file and Z3 constraints from the CFG's paths
class Solver:
    def __init__(self, source, runtime_bytecode):
        cfg = ControlFlowGraph()
        cfg.build(runtime_bytecode)

        self.source = source
        self.cfg = cfg

    def run(self):
        self.cfg.save_control_flow_graph(os.path.splitext(self.source)[0])

def main():
    source = "examples/Addition.sol"
    contract_name = "Addition"
    solc_version = "0.5.5"
    evm_version = "petersburg"

    if source.endswith(".sol"):
        compiler_output = compile(solc_version, evm_version, source)
        if not compiler_output:
            print("No compiler output for: " + source)
        
        for contract_name_item, contract_item in compiler_output['contracts'][source].items():
            if contract_item and contract_name_item != contract_name:
                continue
            if contract_item['evm']['deployedBytecode']['object']:
                solver = Solver(source, contract_item['evm']['deployedBytecode']['object'])
                solver.run()
    else:
        print("Unsupported input file: ", source)
        sys.exit(-1)

if '__main__' == __name__:
    main()
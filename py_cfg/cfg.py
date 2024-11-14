from py2cfg import CFGBuilder

cfg = CFGBuilder().build_from_file('example', 'example.py')
# cfg.build_visual('exampleCFG', 'dot')
cfg.build_visual('exampleCFG', 'pdf')
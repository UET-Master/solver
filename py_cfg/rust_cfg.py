import networkx as nx
import re

def parse_rust_code(rust_code):
    """
    Basic parser to extract control flow elements from Rust code.
    """
    blocks = re.split(r'(?<=\})|(?<=;)', rust_code)  # Split by end of statements or blocks
    parsed_blocks = []
    
    for i, block in enumerate(blocks):
        # Identify statements and create a simplified control block
        if "fn " in block:
            parsed_blocks.append((f"Function_{i}", block))
        elif "if" in block:
            parsed_blocks.append((f"Condition_{i}", block))
        elif "else" in block:
            parsed_blocks.append((f"Else_{i}", block))
        elif "loop" in block or "while" in block:
            parsed_blocks.append((f"Loop_{i}", block))
        else:
            parsed_blocks.append((f"Stmt_{i}", block))

    return parsed_blocks

def build_cfg(parsed_blocks):
    """
    Builds a CFG from parsed Rust code blocks.
    """
    cfg = nx.DiGraph()
    previous_node = None

    for node_id, content in parsed_blocks:
        cfg.add_node(node_id, code=content)
        if previous_node:
            cfg.add_edge(previous_node, node_id)
        previous_node = node_id

    return cfg

def visualize_cfg(cfg):
    """
    Visualizes the control flow graph using networkx and matplotlib.
    """
    import matplotlib.pyplot as plt

    pos = nx.spring_layout(cfg)
    labels = nx.get_node_attributes(cfg, 'code')
    nx.draw(cfg, pos, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)
    plt.show()

# Example Rust code to parse
rust_code = """
fn main() {
    let x = 5;
    if x > 0 {
        println!("Positive");
    } else {
        println!("Non-positive");
    }
    loop {
        break;
    }
}
"""

# Parsing and building CFG
parsed_blocks = parse_rust_code(rust_code)
cfg = build_cfg(parsed_blocks)
visualize_cfg(cfg)

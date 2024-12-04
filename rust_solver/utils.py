import re

# Replace special labels with corresponding labels of Graphviz
def clean_instructions(code):
    code = str(code)
    replacements = {
       '<': '&lt;', 
        '{ ': '&lt;', 
        '>': '&gt;',
        ' }': '&gt;',
        '{}': '\{\}',
        # Remove [`] character in a string like `{} + {}`
        '`': ''
    }
    for old_character, new_character in replacements.items():
        code = code.replace(old_character, new_character)

    # Replace strings like "xxx" with [xxx]
    if re.search(r'"(.*?)"', code):
        code = re.sub(r'"(.*?)"', r'[\1]', code)

    return code
# Replace special labels with corresponding those of Graphviz
def clean_instructions(code):
    code = str(code)
    replacements = {
       '<': '&lt;', 
        '{ ': '&lt;', 
        '>': '&gt;',
        ' }': '&gt;'
    }
    for old_character, new_character in replacements.items():
        code = code.replace(old_character, new_character)

    return code
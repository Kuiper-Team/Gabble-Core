from importlib import import_module
from os import walk

def add_dot(*args):
    result = ""
    for parameter in args:
        if result != "": result += "." + parameter
        else: result += parameter

    return result

def import_directory(path, excluded_directory_names=tuple(), return_imported_scripts=False):
    scripts = []
    recursion_current_directory = ""
    for root, directories, files in walk(path):
        for file in files:
            if file.endswith(".py"): scripts.append(add_dot(recursion_current_directory, file[:-3]))
        for directory in directories:
            if directory not in excluded_directory_names:
                recursion_current_directory = add_dot(recursion_current_directory, directory)
                import_directory(directory, excluded_directory_names=excluded_directory_names)

    for script in scripts: import_module(add_dot(path, script))

    if return_imported_scripts: return scripts
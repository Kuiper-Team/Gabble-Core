from termcolor import colored

def success(text):
    print(colored("SUCCESS: " + text, "white", "on_green"))

def warning(text):
    print(colored("WARNING: " + text, "white", "on_blue"))

def failure(text):
    print(colored("FAILURE: " + text, "white", "on_red"))
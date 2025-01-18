from termcolor import colored

def success(text):
    print(colored("BAŞARILI: " + text, "white", "on_green"))

def warning(text):
    print(colored("UYARI: " + text, "white", "on_blue"))

def failure(text):
    print(colored("BAŞARISIZ: " + text, "white", "on_red"))
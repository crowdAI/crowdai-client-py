from termcolor import colored, cprint


def green(message):
    return colored(message, "green", attrs=['bold'])

def red(message):
    return colored(message, "red", attrs=['bold'])

def yellow(message):
    return colored(message, "yellow", attrs=['bold'])

def blue(message):
    return colored(message, "blue", attrs=['bold'])

def colored_line(event, event_color, message, message_color):
    text = ""
    text += colored(event, event_color, attrs=['bold'])
    if message != "":
        text+=" : "

    if message_color == False:
        text += message
    else:
        text += colored(message, message_color, attrs=['bold'])
    return text

def success(event, message, message_color=False):
    return colored_line(event, "green", message, "green")

def error(event, message, message_color=False):
    return colored_line(event, "red", message, "red")

def info(event, message, message_color=False):
    return colored_line(event, "cyan", message, message_color)

def info_yellow(event, message, message_color=False):
    return colored_line(event, "yellow", message, message_color)

def info_blue(event, message, message_color=False):
    return colored_line(event, "blue", message, message_color)

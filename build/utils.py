# Utility functions for various actions
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

import os
import sys
import time
import shutil
import tarfile
import threading

if sys.platform == 'win32':
    import ctypes

def archive(directory):
    tar_name = os.getcwd()
    if sys.platform == 'win32':
        tar_name = tar_name.replace('\\', '/')
    tar_name = tar_name.split('/')
    tar = tarfile.open(tar_name, 'w:bz2')
    tar.add(directory)
    tar.close()

def clean(directory):
    try:
        shutil.rmdir(directory)
    except:
        cprint('Could not remove object file directory!', red)
        
def wait():
    while threading.active_count() > 1:
        time.sleep(1)

def is_exe(filepath):
    return os.path.exists(filepath) and os.access(filepath, os.X_OK)

def which(program_name):
    if sys.platform == 'win32':
        filepath = os.path.split(program_name + '.exe')[0]
    else:
        filepath = os.path.split(program_name)[0]
    if filepath:
        if is_exe(program_name):
            return program_name
        else:
            for path in os.environ['PATH'].split(os.pathsep):
                if sys.platform == 'win32':
                    exe_file = os.path.join(path, program_name + '.exe')
                else:
                    exe_file = os.path.join(path, program_name)
                if is_exe(exe_file):
                    return exe_file
    return ''
		
if sys.platform == 'win32':
    black   = 0x0000
    blue    = 0x0001
    green   = 0x0002
    cyan    = 0x0003
    red     = 0x0004
    magenta = 0x0005
    yellow  = 0x0006
    white   = 0x0007

else:
    black   = '\33[1;30m'
    blue    = '\33[1;34m'
    green   = '\33[1;32m'
    cyan    = '\33[1;36m'
    red     = '\33[1;31m'
    magenta = '\33[1;35m'
    yellow  = '\33[1;33m'
    white   = '\33[37m'


def cprint(message, color):
    if sys.platform == 'win32':
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        if color == white:
            ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        else:
            ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color|0x0008)
        # A bit hackish, but can be fixed later :)
        print(message),
        ctypes.windll.kernel32.SetConsoleTextAttribute(handle, white) 
        print('')
    else:
        print(color + message + '\33[0m')
    time.sleep(0.1) # This will be removed once Queues are used.
        
def system_type():
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'linux':
        return sys.platform
    elif sys.platform == 'darwin':
        return 'macosx'
    else:
        warning('System not recognized')
        return None

def warning(message):
    cprint(message, yellow)

def error(message):
    cprint(message, red)

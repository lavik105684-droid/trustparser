import os
import sys

def print_debug():
    print("Python Executable:", sys.executable)
    print("Current Working Directory:", os.getcwd())
    print("Directory contents:")
    print(os.listdir("."))
    if os.path.exists("scratch"):
        print("scratch contents:")
        print(os.listdir("scratch"))
    else:
        print("scratch folder does not exist!")

if __name__ == "__main__":
    print_debug()

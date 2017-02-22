# Source: http://stackoverflow.com/a/22006429/2842452, http://stackoverflow.com/a/38656830/2842452
import sys
from cx_Freeze import setup, Executable
import os


os.environ['TCL_LIBRARY'] = r"D:\Program Files\Python35\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"D:\Program Files\Python35\tcl\tk8.6"
includes      = ["tkinter"]
include_files = [r"D:\Program Files\Python35\DLLs\tcl86t.dll", \
                 r"D:\Program Files\Python35\DLLs\tk86t.dll"]

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Categories Backup Tool",
    version = "1.0",
    description = "Tool used to backup or export Steam Categories",
    options = {"build_exe": {"includes": includes, "include_files": include_files}},
    executables = [Executable("GUI.py",targetName="CategoriesBackupTool.exe", base = base)])




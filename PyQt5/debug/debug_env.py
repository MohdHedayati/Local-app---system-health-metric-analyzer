import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}")
print("Sys Path:")
for p in sys.path:
    print(f"  {p}")

try:
    import PyQt5
    print(f"PyQt5 Location: {os.path.dirname(PyQt5.__file__)}")
except ImportError as e:
    print(f"PyQt5 Import Error: {e}")

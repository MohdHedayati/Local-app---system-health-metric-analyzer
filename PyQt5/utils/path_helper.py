import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as EXE, use current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def writable_path(relative_path):
    """ Path to a writable runtime data location under the user's home.
        Use this for files the app needs to create/modify at runtime
        (token.json, history.json, logs, etc.).
    """
    base_dir = os.path.join(os.path.expanduser("~"), ".ai_device_monitor")
    full = os.path.join(base_dir, relative_path)
    directory = os.path.dirname(full)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return full
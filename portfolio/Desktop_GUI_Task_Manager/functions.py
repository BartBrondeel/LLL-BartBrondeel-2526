import os
import sys

# When built as .exe, use the exe location
# When running as .py, use the script location
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILEPATH = os.path.join(BASE_DIR, "files", "todos.txt")


def get_todos(file_path=FILEPATH):
    """ Read a text file and return the list of
    to-do items.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Create the file if it doesn't exist yet
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            pass  # create empty file

    with open(file_path, "r") as file:
        todos_local = file.readlines()
    return todos_local


def write_todos(todos_arg, file_path=FILEPATH):
    """ Write the to-do items list to a text file. """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        file.writelines(todos_arg)

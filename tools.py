import os
import platform
import subprocess
import json

clear_command = 'cls' if os.name == 'nt' else 'clear'


def clear_screen() -> None:
    """ Clear the screen. """
    os.system(clear_command)


if platform.system() == 'Windows':  # Windows
    def open_file(file_path):
        os.startfile(file_path)
elif platform.system() == 'Darwin':  # macOS
    def open_file(file_path):
        subprocess.Popen(['open', file_path])
else:  # linux variants
    def open_file(file_path):
        subprocess.Popen(['xdg-open', file_path])


def ensure_dir_exists(directory) -> None:
    """ Ensure that the directory exists. """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def save_to_file(data_dict, file_path) -> None:
    """ Save the profile to a file. """
    directory = os.path.dirname(file_path)
    ensure_dir_exists(directory)
    with open(file_path, 'w') as file:
        # json.dump(data_dict, file, indent=4)
        if isinstance(data_dict, dict):
            json.dump(data_dict, file, indent=4)
        else:
            file.write(data_dict)

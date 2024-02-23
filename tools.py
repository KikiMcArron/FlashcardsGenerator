import os
import platform
import subprocess

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

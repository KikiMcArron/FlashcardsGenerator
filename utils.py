import json
import os
import platform
# from typing import Dict, List, Optional

import bcrypt

clear_command = 'cls' if os.name == 'nt' else 'clear'


def clear_screen() -> None:
    """ Clear the screen. """
    os.system(clear_command)


def get_default_text_editor() -> str:
    """
    Get the default text editor.

    :return: The default text editor.
    """
    system = platform.system()
    if system == 'Windows':
        return 'notepad'
    elif system == 'Darwin':
        return 'nano'
    elif system == 'Linux':
        return os.getenv('EDITOR', 'nano')
    else:
        raise RuntimeError('Unsupported operating system.')


def _encrypt(secure_txt: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(secure_txt.encode('utf8'), salt)
    return hashed.decode('utf8')


def save_to_file(data_dict, file_path) -> None:
    """ Save the profile to a file. """
    directory = os.path.dirname(file_path)
    _ensure_dir_exists(directory)
    with open(file_path, 'w') as file:
        if isinstance(data_dict, dict):
            json.dump(data_dict, file, indent=4)
        else:
            file.write(data_dict)


def _ensure_dir_exists(directory) -> None:
    """ Ensure that the directory exists. """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

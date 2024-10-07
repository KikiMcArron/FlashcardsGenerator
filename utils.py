import json
import os
import platform

import bcrypt

clear_command = 'cls' if os.name == 'nt' else 'clear'


def clear_screen() -> None:
    os.system(clear_command)


def get_default_text_editor() -> str:

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
    directory = os.path.dirname(file_path)
    ensure_dir_exists(directory)
    with open(file_path, 'w') as file:
        if isinstance(data_dict, dict):
            json.dump(data_dict, file, indent=4)
        else:
            file.write(data_dict)


def ensure_dir_exists(directory) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

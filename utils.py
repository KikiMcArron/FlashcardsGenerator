import json
import os
import platform
from typing import Any, Callable, Dict

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


def save_data_to_file(data: Any, file_path: str, serialize_fn: Callable[[Any, str], None]) -> None:
    dir_path = os.path.dirname(file_path)
    create_directory_if_not_exists(dir_path)
    try:
        serialize_fn(data, dir_path)
    except IOError as e:
        print(f'Saving data to json file failed: {e}')


def create_directory_if_not_exists(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def serialize_dict_to_json(data: Dict, file_path: str) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

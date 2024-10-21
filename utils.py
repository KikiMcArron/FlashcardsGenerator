import json
import os
import platform
import bcrypt
from typing import Any, Callable, Dict

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


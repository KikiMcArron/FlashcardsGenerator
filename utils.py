import json
import os
import platform
from typing import Dict, List, Optional

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


def json_to_list_of_dicts(json_string: Optional[str]) -> List[Dict[str, str]]:
    if not json_string:
        raise ValueError('The provided JSON string is None.')
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f'Error converting JSON to list of dicts: {e}')
        raise ValueError(f'Invalid JSON format: {e}.') from e

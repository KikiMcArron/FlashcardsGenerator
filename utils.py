import json
from typing import List, Dict, Optional


def json_to_list_of_dicts(json_string: Optional[str]) -> List[Dict[str, str]]:
    if not json_string:
        raise ValueError('The provided JSON string is None.')
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f'Error converting JSON to list of dicts: {e}')
        raise ValueError(f'Invalid JSON format: {e}.') from e

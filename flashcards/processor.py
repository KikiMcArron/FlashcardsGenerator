from dataclasses import is_dataclass, fields
from typing import TypeVar, Generic, Optional, List, Dict
import os
import platform
import subprocess
import tempfile


T = TypeVar('T')


class DataclassEditor(Generic[T]):
    """Class for editing dataclasses in a text editor."""

    def __init__(self, editor: Optional[str] = None, display_fields: Optional[List[str]] = None) -> None:
        """
        Initialize the DataclassEditor.

        :param editor: The text editor to use. If None, the default editor will be used.
        :param display_fields: The fields to display in the editor. If None, all fields will be displayed.
        """
        self.display_fields = display_fields
        self.editor = editor if editor else self._get_default_editor()
        self.tmpfields: Dict = {}

    @staticmethod
    def _get_default_editor() -> str:
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

    def _write_dataclass_to_tempfile(self, obj: T) -> str:
        """
        Write the dataclass to a temporary file.

        :param obj: The dataclass object to write to the file.
        :return: The path to the temporary file.
        """
        if not is_dataclass(obj):
            raise ValueError('The provided object is not a dataclass.')

        tmpfile = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        try:
            for field in fields(obj):
                if (self.display_fields is None or field.name in self.display_fields) and field.init is True:
                    value = getattr(obj, field.name)
                    tmpfile.write(f'{field.name.capitalize()}: {value}\n')
                elif field.init is True:
                    value = getattr(obj, field.name)
                    self.tmpfields[field.name] = value
            tmpfile.flush()
            return tmpfile.name
        finally:
            tmpfile.close()

    def _read_dataclass_from_tempfile(self, filepath: str, obj_type: type) -> T:
        """
        Read the dataclass from a temporary file.

        :param filepath: The path to the temporary file.
        :param obj_type: The type of the dataclass object.
        :return: The dataclass object read from the file.
        """
        with open(filepath, 'r') as tmpfile:
            data = {}
            for line in tmpfile:
                name, value = line.strip().split(': ', 1)
                field_name = name.lower()
                data[field_name] = value
        os.remove(filepath)
        return obj_type(**data, **self.tmpfields)

    def edit_dataclass(self, obj: T) -> T:
        """
        Edit the dataclass object in a text editor.

        :param obj: The dataclass object to edit.
        :return: The modified dataclass object.
        """
        obj_file = type(obj)
        filepath = self._write_dataclass_to_tempfile(obj)
        subprocess.run([self.editor, filepath])
        return self._read_dataclass_from_tempfile(filepath, obj_file)

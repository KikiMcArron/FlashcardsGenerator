# Module responsible for managing sources of data.
import json
import os.path


class Source:
    """ Class representing a source of data. """

    def __init__(self, source_type=None, note_name=None, source_path=None) -> None:
        """ Initialize the manager. """
        self.source_type = source_type
        self.note_name = note_name
        self.source_path = source_path

    def __str__(self) -> str:
        """ Return a string representation of the source note. """
        return f'{self.note_name} (Note type: {self.source_type}, note path: {self.source_path})'

    def as_dict(self) -> dict:
        """ Return the source as a dictionary. """
        return {
            'source_type': self.source_type,
            'note_name': self.note_name,
            'source_path': self.source_path
        }


class SourceManager:
    """ Class responsible for managing sources of data. """

    def __init__(self, settings_file='settings.json') -> None:
        """ Initialize the manager. """
        self.current_source = None
        self.settings_file = settings_file
        self.current_source = self.determine_current_source()

    def determine_current_source(self) -> Source:
        """ Determine the current source of data. """
        if not os.path.exists(self.settings_file):
            return None
        with open(self.settings_file, 'r') as file:
            settings = json.load(file)
        current_source_data = settings.get('current_source')
        current_source = Source(**current_source_data)
        return current_source

    def display_source_info(self) -> None:
        """ Display the source information. """
        # TODO: Add condition to check if the current source is None or any source value is None or file does not exist
        if not self.current_source:
            print('>>>>> Current source note: NO NOTE SELECTED <<<<<')
        else:
            print(f'>>>>> Current source note: {self.current_source} <<<<<')

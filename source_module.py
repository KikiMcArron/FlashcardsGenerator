# Module responsible for managing sources of data.

import json
import tkinter as tk
from tkinter import filedialog
from tools import *
from data import file_types


class Source:
    """ Class representing a source note. """

    def __init__(self, source_type=None, note_name=None, source_path=None) -> None:
        """ Initialize the manager. """
        self.source_type = source_type
        self.note_name = note_name
        self.source_path = source_path

    def __str__(self) -> str:
        """ Return a string representation of the source note. """
        return f'{self.note_name.split(sep=".")[0]} (Note type: {self.source_type}, Note path: {self.source_path})'

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
        # self.current_source = None
        self.settings_file = settings_file
        self.current_source = self.determine_current_source()

    def determine_current_source(self) -> Source:
        """ Determine the current source of data. """
        if not os.path.exists(self.settings_file):
            return None
        with open(self.settings_file, 'r') as file:
            settings = json.load(file)
        current_source_data = settings.get('current_source')
        if not current_source_data:
            return None
        current_source = Source(**current_source_data)
        return current_source

    def display_source_info(self) -> None:
        """ Display the source information. """
        # TODO: Add condition to check if the current source is None or any source value is None or file does not exist
        if not self.current_source:
            print('>>>>> Current source note: NO NOTE SELECTED <<<<<')
        else:
            print(f'>>>>> Current source note: {self.current_source} <<<<<')

    def load_note(self) -> None:
        """ Load a note. """
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1]
            self.current_source = Source(file_type, file_name, file_path)
            self.save_current_source()
            print(f'Note loaded: {self.current_source}')
            input('Press Enter to continue...')
            # clear_screen()
            # self.open_note_with_default_app()
            return self.current_source

    def read_note_content(self) -> str:
        """ Read the content of the note. """
        try:
            with open(self.current_source.source_path, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            print(f'Error occurred while reading the note: {e}')
            return None

    def save_current_source(self) -> None:
        """ Save the current source to the settings file. """
        try:
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings['current_source'] = self.current_source.as_dict()

        with open(self.settings_file, 'w') as file:
            json.dump(settings, file, indent=4)

    # def open_note_with_default_app(self) -> None:
    #     """ Open the note with the default application. """
    #     if not self.current_source:
    #         print('No note selected.')
    #         input('Press Enter to continue...')
    #         return
    #     try:
    #         open_file(self.current_source.source_path)
    #     except Exception as e:
    #         print(f"Failed to open file: {e}")

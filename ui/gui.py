import tkinter as tk
from tkinter import filedialog as fd


class FileSelector:
    """
    Class responsible for selecting a file using a GUI.

    :param file_types: A list of file types to allow selection of.
    """
    def __init__(self, file_types: list) -> None:
        self.file_types = file_types
        self.file_path = ''

    def select_file(self) -> str:
        """
        Select a file using a GUI dialog.

        :return: The path to the selected file.
        """
        root = tk.Tk()
        root.withdraw()
        self.file_path = fd.askopenfilename(filetypes=self.file_types)
        return self.file_path

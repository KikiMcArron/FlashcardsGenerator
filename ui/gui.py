import tkinter as tk
from tkinter import filedialog as fd


class FileSelector:
    def __init__(self, file_types: list) -> None:
        self.file_types = file_types
        self.file_path = ''

    def select_file(self) -> str:
        root = tk.Tk()
        root.withdraw()
        self.file_path = fd.askopenfilename(filetypes=self.file_types)
        return self.file_path

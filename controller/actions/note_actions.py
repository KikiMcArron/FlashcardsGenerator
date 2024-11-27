import stdiomask  # type: ignore

from controller.actions.base_action import Action
from notes.reader import TxtReader
from ui.gui import FileSelector
from ui.menu_items import MenuState, StageState
from ui.ui_manager import ContextManager


class NoteFromFile(Action):
    def __init__(self, context_manager: ContextManager, file_selector: FileSelector):
        self.context_manager = context_manager
        self.file_selector = file_selector

    def execute(self):
        self.log('Load note from TXT file...')
        file_path = self.file_selector.select_file()
        if file_path:
            txt_reader = TxtReader()
            content = txt_reader.read_source(file_path)
            self.context_manager.current_note = content
            self.context_manager.current_stage = StageState.NO_CARDS_GENERATED
            self.context_manager.current_menu = MenuState.MAIN_MENU
            self.info('Note loaded successfully!')

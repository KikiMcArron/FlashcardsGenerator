profile_menu_items = {
    'new_profile': '1. Add new profile',
    'select_profile': '2. Select profile',
    'edit_profile': '3. Edit profile',
    'select_source_note': '8. Select source note',
    'exit': '9. Quit program'
}

source_menu_items = {
    'source_file': '1. Select the note file (.txt, .pdf)',
    'source_notion': '2. Select Notion note (coming soon)',
    'generate_cards': '7. Generate flashcards',
    'profile_menu': '8. Back to profile configuration menu',
    'exit': '9. Quit program'
}

module_menus = {
    'profile': profile_menu_items,
    'source': source_menu_items
}

stages = {
    'initiation': ['new_profile', 'exit'],
    'no_profile_selected': ['new_profile', 'select_profile', 'edit_profile', 'exit'],
    'profile_selected': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'exit'],
    'no_note_selected': ['source_file', 'source_notion', 'profile_menu', 'exit'],
    'note_selected': ['source_file', 'source_notion', 'generate_cards', 'profile_menu', 'exit']
}

openai_models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]

file_types = [
    ('Text files', '.txt'),
    ('PDF files', '.pdf'),
    ('All files', '.*')
]

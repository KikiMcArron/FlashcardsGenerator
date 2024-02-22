profile_menu_items = {
    'new_profile': '1. Add new profile',
    'select_profile': '2. Select profile',
    'edit_profile': '3. Edit profile',
    'select_source_note': '8. Select source note',
    'exit': '9. Quit program'
}

source_menu_items = {
    'source_notion': '1. Select Notion note (coming soon)',
    'source_pdf': '2. Select PDF file to load (coming soon)',
    'source_txt': '3. Select TXT file to load',
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
    'no_note_selected': ['source_notion', 'source_pdf', 'source_txt', 'profile_menu', 'exit'],
    'note_selected': ['source_notion', 'source_pdf', 'source_txt', 'generate_cards', 'profile_menu', 'exit']
}

openai_models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]



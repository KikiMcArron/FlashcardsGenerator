STORAGE_DIR = 'storage'
PROFILES_DIR = 'profiles'
USERS_FILE = 'users.json'


FILE_TYPES = [
    ('Text files', '.txt'),
    ('PDF files', '.pdf'),
    ('All files', '.*')
]

OPENAI_MODELS = ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-turbo-preview']

PROMPT = (
                f'Generate flashcards for the given text, based on content and information from text. '
                f'Please format the flashcards as a simple JSON array with keys: "front", "back", '
                f'without Markdown or code block formatting.'
            )

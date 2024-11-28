
# Flashcards Generator

Flashcards Generator is a Python-based application designed to help users create, organize, and review flashcards. 
It also supports managing  user profiles to provide a personalized usage experience.

## Features

- **User management**: Create and manage Users, Profiles and Credentials.
- **Notes Integration**: Load notes of different type (.txt for now, **MORE COMING SOON**).
- **Flashcards generation**: Generate flashcards from note using AI models.
- **Flashcards review**: Approve, reject or edit generated flashcards one-by-one.
- **Export Flashcards**: Export flashcards to various formats. (**COMING SOON**)

## Project Structure

- **app.py**: Entry point of the application.
- **settings.py**: Configuration and settings.
- **logger.py**: Handles logging for the application.
- **custom_exceptions.py**: Defines custom exceptions for better error handling.
- **utils.py**: Utility functions used across the project.

### Core Modules

- **controller/**: Handles control flow of application endpoints.
- **controller/actions/**: Contains service-related actions and logic.
- **flashcards/**: Logic and data handling for flashcards.
- **notes/**: Manages source note.
- **profiles/**: Deals with user profiles and settings.

### User Interface

- **ui/**: User interface components.

### Testing

- **tests/**: Contains unit and integration tests.

## Requirements

To run the project, ensure you have the following installed:

- Python 3.8 or later
- Required dependencies (listed in `requirements.txt`)

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Usage

### Run the application:

```bash
python app.py
```

### Application Flow

**1. Login Menu:**
    - On application launch, the logging menu is displayed.
    - Here, you can create and manage users and log in to the application.

**2. Main Menu:**
    - After logging in, the main menu appears, guiding you through the process step-by-step:
        - Create a profile.
        - Configure the AI model.
        - Select a note.
        - Generate flashcards.
        - Review, approve, or edit the generated cards.

**3. Data Persistence:**
    - All credentials and user settings are saved on the fly, so there's no need to reconfigure them every time.



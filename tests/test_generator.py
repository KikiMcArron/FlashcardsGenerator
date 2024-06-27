import pytest
from unittest.mock import MagicMock, patch
from flashcards.generator import OpenAIClient, CardsGenerator


# Fixtures for setting up mocks and objects

@pytest.fixture
def api_key():
    return 'test_api_key'


@pytest.fixture
def mock_openai_client(api_key):
    with patch('flashcards.generator.OpenAI') as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.api_key = api_key
        yield mock_client


@pytest.fixture
def openai_client(api_key, mock_openai_client):
    return OpenAIClient(api_key)


@pytest.fixture
def cards_generator(openai_client):
    return CardsGenerator(ai_client=openai_client)


# Tests for OpenAIClient

def test_openai_client_initialization(api_key):
    client = OpenAIClient(api_key)
    assert str(client) == f'OpenAI client (API Key: {api_key[:3]}...{api_key[-4:]})'


def test_generate_completion_success(openai_client, mock_openai_client):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = 'Test content'
    mock_openai_client.chat.completions.create.return_value = mock_response

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Generate flashcards for the given text."}
    ]
    response = openai_client.generate_completion('test_model', messages)

    assert response == 'Test content'
    mock_openai_client.chat.completions.create.assert_called_once_with(
        model='test_model',
        messages=messages,
        max_tokens=1000,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.0
    )


def test_generate_completion_failure(openai_client, mock_openai_client):
    mock_openai_client.chat.completions.create.side_effect = Exception('API error')
    with pytest.raises(Exception) as exc_info:
        openai_client.generate_completion('test_model', [])
    assert 'API error' in str(exc_info.value)
    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="test_model",
        messages=[],
        max_tokens=1000,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.0,
    )


# Tests for CardsGenerator

def test_generate_flashcards_success(cards_generator, mock_openai_client):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = 'Test content'
    mock_openai_client.chat.completions.create.return_value = mock_response

    model = 'test_model'
    prompt = 'Generate flashcards'
    content = 'Some text content to generate flashcards from.'
    response = cards_generator.generate_flashcards(model, prompt, content)

    assert response == 'Test content'
    mock_openai_client.chat.completions.create.assert_called_once()


def test_generate_flashcards_failure(cards_generator, mock_openai_client):
    mock_openai_client.chat.completions.create.side_effect = Exception('API call failed')

    model = 'test_model'
    prompt = 'Generate flashcards'
    content = 'Some text content to generate flashcards from.'

    with pytest.raises(Exception, match='API call failed'):
        cards_generator.generate_flashcards(model, prompt, content)

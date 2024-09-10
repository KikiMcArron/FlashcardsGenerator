from profiles.credentials import OpenAICredentials


def test_service_name_is_set_correctly():
    creds = OpenAICredentials(api_key='my_api_key', gpt_model='gpt-3')
    assert creds.service_name == 'OpenAI'


def test_api_key_encryption():
    creds = OpenAICredentials(api_key='my_api_key', gpt_model='gpt-3')
    assert creds.api_key != 'my_api_key'
    assert creds.encrypt_api_key != 'my_api_key'


def test_encrypted_api_key_hidden_in_repr():
    creds = OpenAICredentials(api_key='my_api_key', gpt_model='gpt-3')
    assert 'encrypted_api_key' not in repr(creds)

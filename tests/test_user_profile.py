from unittest.mock import patch

import pytest

from custom_exceptions import DuplicateProfileError, DuplicateServiceError, NoCredentialsError, NoProfileError
from profiles.user_profile import Profile, User


class Credentials:
    def __init__(self, service_name, username, password):
        self.service_name = service_name
        self.username = username
        self.password = password


@pytest.fixture
def sample_credentials():
    return Credentials(service_name='email', username='user@example.com', password='password123')


@pytest.fixture
def another_credentials():
    return Credentials(service_name='cloud', username='user2@example.com', password='password456')


@pytest.fixture
def profile():
    return Profile(profile_name='main')


@pytest.fixture
def user():
    with patch('profiles.user_profile._encrypt', return_value='encrypted_password'):
        return User(user_name='test_user', password='password123')


# Test Cases fpr Profile class #


def test_add_credentials_success(profile, sample_credentials):
    profile.add_credentials(sample_credentials)
    assert sample_credentials in profile.credentials


def test_add_duplicate_credentials_raise_error(profile, sample_credentials):
    profile.add_credentials(sample_credentials)
    with pytest.raises(DuplicateServiceError, match='Credentials for service email already exist in profile main'):
        profile.add_credentials(sample_credentials)


def test_remove_credentials_success(profile, sample_credentials):
    profile.add_credentials(sample_credentials)
    profile.remove_credentials(sample_credentials)
    assert sample_credentials not in profile.credentials


def test_remove_nonexistent_credentials_raise_error(profile, sample_credentials):
    with pytest.raises(NoCredentialsError, match='Credentials not found in profile main'):
        profile.remove_credentials(sample_credentials)


# Test Cases for User class #

def test_user_initialization(user):
    assert user.user_name == 'test_user'
    assert user.is_logged_in is False
    assert user.profiles == []
    assert user.password == 'encrypted_password'


def test_check_password_success(user):
    with patch('bcrypt.checkpw', return_value=True):
        assert user.check_password('password123') is True


def test_check_password_failure(user):
    with patch('bcrypt.checkpw', return_value=False):
        assert user.check_password('wrong_password') is False


def test_add_profile_success(user, profile):
    user.add_profile(profile)
    assert profile in user.profiles


def test_add_duplicate_profile_raise_error(user, profile):
    user.add_profile(profile)
    with pytest.raises(DuplicateProfileError, match='Profile main already exists for User test_user'):
        user.add_profile(profile)


def test_remove_profile_success(user, profile):
    user.add_profile(profile)
    user.remove_profile(profile)
    assert profile not in user.profiles


def test_remove_nonexistent_profile_raises_error(user, profile):
    with pytest.raises(NoProfileError, match="Profile main does not exist for user test_user"):
        user.remove_profile(profile)

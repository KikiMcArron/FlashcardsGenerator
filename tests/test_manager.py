from unittest.mock import MagicMock, patch

import pytest

from custom_exceptions import InvalidPassword, InvalidUsername, UsernameAlreadyExists, ValidationError
from profiles.manager import PasswordValidator, UserManager
from profiles.user_profile import User


@pytest.fixture
def mock_user():
    mock = MagicMock(spec=User)
    mock.check_password.return_value = True
    mock.is_logged_in = False
    return mock


# Test Cases for PasswordValidator

@pytest.fixture
def password_validator_no_max_length():
    return PasswordValidator(min_length=6, max_length=None, numbers=True, special=True, upper_lower=True)


@pytest.fixture
def password_validator():
    return PasswordValidator(min_length=6, max_length=12, numbers=True, special=True, upper_lower=True)


def test_valid_password(password_validator):
    valid_password = "Password1!"
    assert password_validator.is_valid(valid_password) is True


def test_password_too_short(password_validator_no_max_length):
    short_password = "Pw1!"
    with pytest.raises(ValidationError, match="Password length should be at least 6 characters"):
        password_validator_no_max_length.is_valid(short_password)


def test_password_too_long(password_validator):
    long_password = "Password12345!"
    with pytest.raises(ValidationError, match="Password length have to be between 6 and 12 characters"):
        password_validator.is_valid(long_password)


def test_password_missing_number(password_validator):
    password = "Password!"
    with pytest.raises(ValidationError, match="Password must contain at least one number"):
        password_validator.is_valid(password)


def test_password_missing_special_character(password_validator):
    password = "Password1"
    with pytest.raises(ValidationError, match="Password must contain at least one special character"):
        password_validator.is_valid(password)


def test_password_missing_upper_lower(password_validator):
    password = "password1!"
    with pytest.raises(ValidationError, match="Password must contain at least one lowercase and one uppercase letter"):
        password_validator.is_valid(password)


def test_password_with_whitespace(password_validator):
    password = "Password 1!"
    with pytest.raises(ValidationError, match="Password cannot contain whitespaces"):
        password_validator.is_valid(password)


# Test Cases for UserManager

@pytest.fixture
def user_manager(password_validator):
    return UserManager(password_validator)


def test_add_user_success(user_manager, mock_user):
    with patch('profiles.user_profile.User', return_value=mock_user):
        user_manager.add_user('new_user', 'Password1!')
    assert 'new_user' in user_manager.users


def test_add_user_duplicate_username(user_manager, mock_user):
    with patch('profiles.user_profile.User', return_value=mock_user):
        user_manager.add_user('new_user', 'Password1!')
        with pytest.raises(UsernameAlreadyExists, match='Username new_user already exists'):
            user_manager.add_user('new_user', 'Password1!')


def test_add_user_invalid_password(user_manager):
    with patch('profiles.user_profile.User'):
        with pytest.raises(ValueError,
                           match='Password validation failed: Password length have to be between 6 and 12 characters'):
            user_manager.add_user('new_user', 'Pw1!')


def test_remove_user_success(user_manager, mock_user):
    with patch('profiles.user_profile.User', return_value=mock_user):
        user_manager.add_user('new_user', 'Password1!')
        user_manager.remove_user('new_user')
    assert 'new_user' not in user_manager.users


def test_remove_nonexistent_user(user_manager):
    with pytest.raises(InvalidUsername, match="User non_existent does not exist"):
        user_manager.remove_user('non_existent')


def test_login_user_success(user_manager, mock_user):
    with patch('profiles.user_profile.User', return_value=mock_user):
        user_manager.add_user('new_user', 'Password1!')
        user_manager.login_user('new_user', 'Password1!')
        assert user_manager.users['new_user'].is_logged_in is True


def test_login_user_invalid_username(user_manager):
    with pytest.raises(InvalidUsername, match="non_existent"):
        user_manager.login_user('non_existent', 'Password1!')


def test_login_user_invalid_password(user_manager, mock_user):
    mock_user.check_password.return_value = False
    with patch('profiles.user_profile.User', return_value=mock_user):
        user_manager.add_user('new_user', 'Password1!')
        with pytest.raises(InvalidPassword):
            user_manager.login_user('new_user', 'WrongPassword!')


def test_logout_all_users(user_manager, mock_user):
    with patch('profiles.user_profile.User', return_value=mock_user):
        user_manager.add_user('user1', 'Password1!')
        user_manager.add_user('user2', 'Password1!')
        user_manager.login_user('user1', 'Password1!')
        assert user_manager.users['user1'].is_logged_in is True
        assert user_manager.users['user2'].is_logged_in is False
        user_manager.login_user('user2', 'Password1!')
        assert user_manager.users['user1'].is_logged_in is False
        assert user_manager.users['user2'].is_logged_in is True

from dataclasses import dataclass, field
from typing import List

import bcrypt

from custom_exceptions import (DuplicateProfileError, DuplicateServiceError, NoCredentialsError, NoProfileError)
from profiles.credentials import Credentials
from utils import _encrypt


@dataclass
class Profile:
    profile_name: str = 'main'
    credentials: List[Credentials] = field(default_factory=list)

    def add_credentials(self, credentials: Credentials) -> None:
        if any(c.service_name == credentials.service_name for c in self.credentials):
            raise DuplicateServiceError(f'Credentials for service {credentials.service_name} already exist in profile'
                                        f' {self.profile_name}.')
        self.credentials.append(credentials)

    def remove_credentials(self, credentials: Credentials) -> None:
        try:
            self.credentials.remove(credentials)
        except ValueError:
            raise NoCredentialsError(f'Credentials not found in profile {self.profile_name}.')


class User:
    def __init__(self, user_name: str, password: str) -> None:
        self.user_name = user_name
        self.password = _encrypt(password)
        self.profiles: List[Profile] = []
        self.is_logged_in = False

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf8'), self.password.encode('utf8'))

    def add_profile(self, profile: Profile) -> None:
        if any(p.profile_name == profile.profile_name for p in self.profiles):
            raise DuplicateProfileError(f'Profile {profile.profile_name} already exists for User {self.user_name}')
        self.profiles.append(profile)

    def remove_profile(self, profile: Profile) -> None:
        try:
            self.profiles.remove(profile)
        except ValueError:
            raise NoProfileError(f'Profile {profile.profile_name} does not exist for user {self.user_name}')

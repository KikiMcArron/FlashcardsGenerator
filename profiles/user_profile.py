from dataclasses import dataclass, field
from typing import List

from custom_exceptions import DuplicateProfileError, DuplicateServiceError, NoCredentialsError, NoProfileError
from profiles.credentials import Credentials


@dataclass
class Profile:
    profile_name: str = 'main'
    credentials: List[Credentials] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            'profile_name': self.profile_name,
            'credentials': [credentials.as_dict() for credentials in self.credentials]
        }

    @classmethod
    def from_dict(cls, data: dict):
        profile = cls(
            profile_name=data['profile_name'],
        )
        for cred_data in data.get('credentials', []):
            profile.add_credentials(Credentials.from_dict(cred_data))
        return profile

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
    def __init__(self, user_name: str, encrypted_password: str) -> None:
        self.user_name = user_name
        self.encrypted_password = encrypted_password
        self.profiles: List[Profile] = []
        self.is_logged_in = False

    def as_dict(self) -> dict:
        return {
            'user_name': self.user_name,
            'encrypted_password': self.encrypted_password,
            'profiles': [profile.as_dict() for profile in self.profiles]
        }

    @classmethod
    def from_dict(cls, data: dict):
        user = cls(
            user_name=data['user_name'],
            encrypted_password=data['encrypted_password']
        )
        for profile_data in data.get('profiles', []):
            user.add_profile(Profile.from_dict(profile_data))
        return user

    def add_profile(self, profile: Profile) -> None:
        if any(p.profile_name == profile.profile_name for p in self.profiles):
            raise DuplicateProfileError(f'Profile {profile.profile_name} already exists for User {self.user_name}')
        self.profiles.append(profile)

    def remove_profile(self, profile: Profile) -> None:
        try:
            self.profiles.remove(profile)
        except ValueError:
            raise NoProfileError(f'Profile {profile.profile_name} does not exist for user {self.user_name}')

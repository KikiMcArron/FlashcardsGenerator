from dataclasses import dataclass, field
from typing import List, Optional

from custom_exceptions import DuplicateProfileError, DuplicateServiceError, NoCredentialsError, NoProfileError
from profiles.credentials import Credentials, CredentialsFactory


@dataclass
class Profile:
    profile_name: str
    credentials: List[Credentials] = field(default_factory=list)
    default_ai: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            'profile_name': self.profile_name,
            'credentials': [credentials.as_dict() for credentials in self.credentials],
            'default_ai': self.default_ai
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        profile = cls(
            profile_name=data['profile_name'],
            default_ai=data['default_ai']
        )
        for cred_data in data.get('credentials', []):
            credentials = CredentialsFactory.from_dict(cred_data)
            if credentials:
                profile.add_credentials(credentials)
            else:
                raise NoCredentialsError(f"Invalid credentials data encountered {cred_data}")
        return profile

    def add_credentials(self, credentials: Credentials) -> None:
        if any(c.service_name == credentials.service_name for c in self.credentials):
            raise DuplicateServiceError(f'Credentials for service {credentials.service_name} already exist in profile'
                                        f' {self.profile_name}.')
        if credentials.credentials_type == 'AI' and not any(c.credentials_type == 'AI' for c in self.credentials):
            self.set_as_default_ai(credentials)
            print(f'Default AI for this profile updated to {self.default_ai}')
        self.credentials.append(credentials)

    def remove_credentials(self, credentials: Credentials) -> None:
        try:
            self.credentials.remove(credentials)
            if credentials.service_name == self.default_ai:
                self.default_ai = next((c.service_name for c in self.credentials if c.credentials_type == 'AI'), None)
                print(f'Default AI for this profile updated to {self.default_ai}')
        except ValueError:
            raise NoCredentialsError(f'Credentials not found in profile {self.profile_name}.')

    def get_credentials(self, service_name):
        try:
            return next(c for c in self.credentials if c.service_name == service_name)
        except StopIteration:
            raise NoCredentialsError(f'Credentials "{service_name}" does not exists for profile {self.profile_name}.')

    def set_as_default_ai(self, credentials: Credentials) -> None:
        if credentials.credentials_type != 'AI':
            raise ValueError(f'Service {credentials.service_name} is not a valid AI credential.')
        self.default_ai = credentials.service_name


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
    def from_dict(cls, data: dict) -> 'User':
        user = cls(
            user_name=data['user_name'],
            encrypted_password=data['encrypted_password']
        )
        for profile_data in data.get('profiles', []):
            user.add_profile(Profile.from_dict(profile_data))
        return user

    def add_profile(self, profile: Profile) -> None:
        if self.profile_exists(profile.profile_name):
            raise DuplicateProfileError(f'Profile {profile.profile_name} already exists for User {self.user_name}')
        self.profiles.append(profile)

    def remove_profile(self, profile_name: str) -> None:
        profile = self.get_profile(profile_name)
        self.profiles.remove(profile)

    def get_profile(self, profile_name: str) -> Profile:
        try:
            return next(p for p in self.profiles if p.profile_name == profile_name)
        except StopIteration:
            raise NoProfileError(f'Profile "{profile_name}" does not exists for user {self.user_name}.')

    def profile_exists(self, profile_name: str) -> bool:
        return any(p.profile_name == profile_name for p in self.profiles)

from abc import ABC, abstractmethod


class Action(ABC):
    @abstractmethod
    def execute(self):
        pass

    @staticmethod
    def log(message):
        print(f'[LOG] {message}')

    @staticmethod
    def error(message):
        print(f'[ERROR] {message}')
        input('Press enter to continue...')

    @staticmethod
    def info(message):
        print(f'[INFO] {message}')
        input('Press enter to continue...')

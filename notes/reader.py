from abc import ABC, abstractmethod


# import PyPDF2


class BaseReader(ABC):

    @abstractmethod
    def read(self, source: str) -> str:
        pass


class TxtReader(BaseReader):

    def read(self, source: str) -> str:
        with open(source, 'r') as file:
            return file.read()


# TODO: Implement logic for reading notes from PDF files
class PdfReader(BaseReader):
    def read(self, source: str) -> str:
        with open(source, 'r') as file:
            return ''


# TODO: Implement logic for reading notes from DOCX files
class DocxReader(BaseReader):
    def read(self, source: str) -> str:
        with open(source, 'r') as file:
            return ''


# TODO: Implement logic for reading notes from services via API
class ViaAPIReader(BaseReader):
    def __init__(self, api_service):
        self.api_service = api_service

    def read(self, source: str) -> str:
        return ''

from abc import ABC, abstractmethod


# import PyPDF2


class BaseReader(ABC):

    @abstractmethod
    def read_source(self, source: str) -> str:
        pass


class TxtReader(BaseReader):

    def read_source(self, source: str) -> str:
        with open(source, 'r') as file:
            content = file.read()
            return content


# TODO: Implement logic for reading notes from PDF files
class PdfReader(BaseReader):
    def read_source(self, source: str) -> str:
        with open(source, 'r') as file:
            return ''


# TODO: Implement logic for reading notes from DOCX files
class DocxReader(BaseReader):
    def read_source(self, source: str) -> str:
        with open(source, 'r') as file:
            return ''


# TODO: Implement logic for reading notes from services via API
class ViaAPIReader(BaseReader):
    def __init__(self, api_service):
        self.api_service = api_service

    def read_source(self, source: str) -> str:
        return ''

from abc import ABC, abstractmethod


# import PyPDF2


class BaseReader(ABC):
    """Abstract base class for readers"""

    @abstractmethod
    def read(self, source: str) -> str:
        """
        Read the contents of the source file.

        :param source: The path to the source file.
        :return: The contents of the source file.
        """
        pass


class TxtReader(BaseReader):
    """Class for reading text files"""

    def read(self, source: str) -> str:
        """
        Read the contents of the text file.

        :param source: The path to the text file.
        :return: The contents of the text file.
        """
        with open(source, 'r') as file:
            return file.read()


# TODO: Implement logic for reading notes from PDF files
class PdfReader(BaseReader):
    def read(self, source: str) -> str:
        """
        Read the contents of the PDF file.

        :param source: The path to the PDF file.
        :return: The contents of the PDF file.
        """
        with open(source, 'r') as file:
            return ''


# TODO: Implement logic for reading notes from DOCX files
class DocxReader(BaseReader):
    def read(self, source: str) -> str:
        """
        Read the contents of the DOCX file.

        :param source: The path to the DOCX file.
        :return: The contents of the DOCX file.
        """
        with open(source, 'r') as file:
            return ''


# TODO: Implement logic for reading notes from services via API
class APIReader(BaseReader):
    def __init__(self, api_service):
        self.api_service = api_service

    def read(self, source: str) -> str:
        return ''

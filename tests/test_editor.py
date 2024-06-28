import os
import tempfile
from dataclasses import dataclass, field
from unittest.mock import mock_open, patch

import pytest

from flashcards.editor import DataclassEditor


@dataclass
class SampleDataClass:
    internal_id: str = field(init=False, default='12345')
    name: str
    age: int
    email: str


# Test initialization of DataclassEditor

def mock_get_default_text_editor():
    return "mock_editor"


def test_dataclass_editor_default_initialization(monkeypatch):
    monkeypatch.setattr("flashcards.editor.get_default_text_editor", mock_get_default_text_editor)

    editor = DataclassEditor()
    assert editor.text_editor == "mock_editor"
    assert editor.display_fields is None


def test_dataclass_editor_specified_text_editor():
    custom_editor = "custom_editor"
    editor = DataclassEditor(text_editor=custom_editor)
    assert editor.text_editor == custom_editor
    assert editor.display_fields is None


def test_dataclass_editor_default_display_fields():
    editor = DataclassEditor()
    assert editor.display_fields is None


def test_dataclass_editor_specified_display_fields(monkeypatch):
    monkeypatch.setattr("flashcards.editor.get_default_text_editor", mock_get_default_text_editor)
    display_fields = ["field1", "field2"]
    editor = DataclassEditor(display_fields=display_fields)
    assert editor.text_editor == 'mock_editor'
    assert editor.display_fields == display_fields


# Test writing a dataclass to a temporary file
def test_write_dataclass_to_tmpfile_not_dataclass():
    editor = DataclassEditor()
    with pytest.raises(ValueError, match='The provided object is not a dataclass.'):
        editor._write_dataclass_to_tmpfile('not_a_dataclass')


def test_write_dataclass_to_all_fields():
    editor = DataclassEditor()
    obj = SampleDataClass(name='John Doe', age=30, email='john.doe@example.com')
    filepath = editor._write_dataclass_to_tmpfile(obj)
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        expected_content = 'Name: John Doe\nAge: 30\nEmail: john.doe@example.com\n'
        assert content == expected_content
    finally:
        os.remove(filepath)


def test_write_dataclass_to_tmpfile_display_fields():
    editor = DataclassEditor(display_fields=['name', 'email'])
    obj = SampleDataClass(name='John Doe', age=30, email='john.doe@example.com')
    filepath = editor._write_dataclass_to_tmpfile(obj)
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        expected_content = 'Name: John Doe\nEmail: john.doe@example.com\n'
        assert content == expected_content
    finally:
        os.remove(filepath)


def test_write_dataclass_to_tmpfile_exclude_non_init_fields():
    editor = DataclassEditor()
    obj = SampleDataClass(name='John Doe', age=30, email='john.doe@example.com')
    filepath = editor._write_dataclass_to_tmpfile(obj)
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        assert 'Internal_id: 12345' not in content
        expected_content = 'Name: John Doe\nAge: 30\nEmail: john.doe@example.com\n'
        assert content == expected_content
    finally:
        os.remove(filepath)


# Test reading dataclass from temporary file

@pytest.fixture
def sample_tmpfile_all_fields():
    content = 'Name: John Doe\nAge: 30\nEmail: john.doe@example.com\n'
    tmpfile = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    try:
        tmpfile.write(content)
        tmpfile.flush()
        tmpfile.close()
        yield tmpfile.name
    finally:
        try:
            os.remove(tmpfile.name)
        except FileNotFoundError:
            pass


@pytest.fixture
def sample_tmpfile_display_fields():
    content = 'Name: John Doe\nEmail: john.doe@example.com\n'
    tmpfile = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    try:
        tmpfile.write(content)
        tmpfile.flush()
        tmpfile.close()
        yield tmpfile.name
    finally:
        try:
            os.remove(tmpfile.name)
        except FileNotFoundError:
            pass


def test_read_dataclass_from_tmpdile_all_fields(sample_tmpfile_all_fields):
    editor = DataclassEditor()
    obj = editor._read_dataclass_from_tmpfile(sample_tmpfile_all_fields, SampleDataClass)
    assert obj.name == 'John Doe'
    assert obj.age == '30'
    assert obj.email == 'john.doe@example.com'
    assert obj.internal_id == '12345'


def test_read_dataclass_from_tmpfile_display_fields(sample_tmpfile_display_fields):
    editor = DataclassEditor(display_fields=['name', 'email'])
    editor.tmpfields = {'age': 30}
    obj = editor._read_dataclass_from_tmpfile(sample_tmpfile_display_fields, SampleDataClass)
    assert obj.name == 'John Doe'
    assert obj.email == 'john.doe@example.com'
    assert obj.internal_id == '12345'
    assert obj.age == 30


# Test editing dataclass

class NamedTemporaryFileMock:
    def __init__(self, mode='w+', delete=True, name=None):
        self.name = name if name else tempfile.mktemp()
        self.file = open(self.name, mode)
        self.delete = delete

    def write(self, data):
        self.file.write(data)

    def flush(self):
        self.file.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        if not self.file.closed:
            self.file.close()
        if self.delete and os.path.exists(self.name):
            os.remove(self.name)


def test_edit_dataclass_all_fields():
    editor = DataclassEditor()
    obj = SampleDataClass(name="John Doe", age=30, email="john.doe@example.com")

    mock_tempfile_content = "Name: Jane Doe\nAge: 40\nEmail: jane.doe@example.com\n"
    tmpfile_name = '/tmp/tmpfile_all_fields'

    tmpfile_mock = NamedTemporaryFileMock(delete=False, name=tmpfile_name)
    with tmpfile_mock as tmpfile:
        tmpfile.write(mock_tempfile_content)
        tmpfile.flush()
    def mock_subprocess_run(cmd):
        with open(cmd[1], 'w') as f:
            f.write(mock_tempfile_content)

    with patch("flashcards.editor.tempfile.NamedTemporaryFile", return_value=tmpfile_mock), \
         patch("flashcards.editor.subprocess.run", side_effect=mock_subprocess_run) as mock_run, \
         patch("builtins.open", mock_open(read_data=mock_tempfile_content)):
        edited_obj = editor.edit_dataclass(obj)

        mock_run.assert_called_once_with([editor.text_editor, tmpfile_name])

        assert edited_obj.name == "Jane Doe"
        assert edited_obj.age == '40'
        assert edited_obj.email == "jane.doe@example.com"
        assert edited_obj.internal_id == "12345"

    tmpfile_mock.close()


def test_edit_dataclass_with_display_fields():
    editor = DataclassEditor(display_fields=["name", "email"])
    obj = SampleDataClass(name="John Doe", age=30, email="john.doe@example.com")

    mock_tempfile_content = "Name: Jane Doe\nEmail: jane.doe@example.com\n"
    tmpfile_name = '/tmp/tmpfile_with_display_fields'

    tmpfile_mock = NamedTemporaryFileMock(delete=False, name=tmpfile_name)
    with tmpfile_mock as tmpfile:
        tmpfile.write(mock_tempfile_content)
        tmpfile.flush()

    def mock_subprocess_run(cmd):
        with open(cmd[1], 'w') as f:
            f.write(mock_tempfile_content)

    with patch("flashcards.editor.tempfile.NamedTemporaryFile", return_value=tmpfile_mock), \
         patch("flashcards.editor.subprocess.run", side_effect=mock_subprocess_run) as mock_run, \
         patch("builtins.open", mock_open(read_data=mock_tempfile_content)):
        editor.tmpfields = {'age': 30}

        edited_obj = editor.edit_dataclass(obj)

        mock_run.assert_called_once_with([editor.text_editor, tmpfile_name])

        assert edited_obj.name == "Jane Doe"
        assert edited_obj.email == "jane.doe@example.com"
        assert edited_obj.internal_id == "12345"
        assert edited_obj.age == 30

    tmpfile_mock.close()


def test_edit_dataclass_missing_required_field():
    editor = DataclassEditor(display_fields=["name"])
    obj = SampleDataClass(name="John Doe", age=30, email="john.doe@example.com")

    mock_tempfile_content = "Name: Jane Doe\n"
    tmpfile_name = '/tmp/tmpfile_missing_required_field'

    tmpfile_mock = NamedTemporaryFileMock(delete=False, name=tmpfile_name)
    with tmpfile_mock as tmpfile:
        tmpfile.write(mock_tempfile_content)
        tmpfile.flush()

    def mock_subprocess_run(cmd):
        with open(cmd[1], 'w') as f:
            f.write(mock_tempfile_content)

    with patch("flashcards.editor.tempfile.NamedTemporaryFile", return_value=tmpfile_mock), \
         patch("flashcards.editor.subprocess.run", side_effect=mock_subprocess_run) as mock_run, \
         patch("builtins.open", mock_open(read_data=mock_tempfile_content)):
        editor.tmpfields = {'age': 30, 'email': "john.doe@example.com"}

        edited_obj = editor.edit_dataclass(obj)

        mock_run.assert_called_once_with([editor.text_editor, tmpfile_name])

        assert edited_obj.name == "Jane Doe"
        assert edited_obj.internal_id == "12345"
        assert edited_obj.age == 30
        assert edited_obj.email == "john.doe@example.com"

    tmpfile_mock.close()

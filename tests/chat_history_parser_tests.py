import pytest
import json
import os
from unittest.mock import patch
from src.settings import SESSIONS_PATH
from src.services.chat_history_parser import ChatHistoryParser


@pytest.fixture
def mock_chat_history():
    """Fixture that provides a mock chat history."""
    return [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi, how can I help you today?"}
    ]


@pytest.fixture
def file_name():
    """Fixture that provides a sample file name for saving/loading."""
    return "test_chat_history.json"


@pytest.fixture
def chat_history_parser():
    """Fixture that creates an instance of ChatHistoryParser."""
    return ChatHistoryParser(folder_path=SESSIONS_PATH)


def test_save_to_json(chat_history_parser, mock_chat_history, file_name):
    """Test saving chat history to a JSON file."""
    chat_history_parser.save_to_json(mock_chat_history, file_name)

    file_path = f'{SESSIONS_PATH}/{file_name}'
    assert os.path.exists(file_path), "The JSON file was not created."

    with open(file_path, 'r') as f:
        saved_history = json.load(f)
    assert saved_history == mock_chat_history, "The saved chat history doesn't match the expected history."


def test_load_from_json(chat_history_parser, mock_chat_history, file_name):
    """Test loading chat history from a JSON file."""
    chat_history_parser.save_to_json(mock_chat_history, file_name)
    loaded_history = chat_history_parser.load_from_json(file_name)
    assert loaded_history == mock_chat_history, "The loaded chat history doesn't match the saved history."

def test_load_from_json_raises_file_not_found_error(chat_history_parser):
    """Test that FileNotFoundError is raised when trying to load from a non-existent file."""
    file_name = "non_existent_file.json"
    with pytest.raises(FileNotFoundError,
                       match=f"No existing chat history found at {chat_history_parser.folder_path}/{file_name}"):
        chat_history_parser.load_from_json(file_name)

@pytest.fixture
def empty_file(chat_history_parser, file_name):
    """Fixture to create an empty file for testing."""
    file_path = f'{chat_history_parser.folder_path}/{file_name}'
    with open(file_path, 'w') as f:
        f.write('')
    return file_path

def test_load_from_json_raises_value_error_for_empty_file(chat_history_parser, empty_file, file_name):
    """Test that ValueError is raised when trying to load an empty JSON file."""

    with pytest.raises(ValueError, match=f"The chat history file does not contain a valid list of messages."):
        chat_history_parser.load_from_json(file_name)
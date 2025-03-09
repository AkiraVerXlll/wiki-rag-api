from typing import List
import json
import os

class ChatHistoryParser:
    """
        A class responsible for saving and loading chat history from JSON files.
    """

    def __init__(self, folder_path: str):
        """
        Initialize the ChatHistoryParser with a file path for saving and loading chat history.

        :param folder_path: str
            The directory where the chat history JSON files will be saved or loaded from.
        """
        self.folder_path = folder_path

    def is_file_exists(self, session_id: str) -> bool:
        """
        Check if a file with the specified session ID exists in the given folder.

        :param session_id: str
            The name of the file to check for existence.

        :return: bool
            True if the file exists, False otherwise.
        """
        return os.path.exists(f'{self.folder_path}/{session_id}')

    def save_to_json(self, chat_history: list[dict[str, str]], file_name: str):
        """
        Save the chat history to a JSON file.

        :param chat_history: List[Dict[str, str]]
            A list of dictionaries representing the chat history. Each dictionary contains a "role" and "content".
        :param file_name: str
            The name of the file to save the chat history to.
        """
        with open(f'{self.folder_path}/{file_name}', 'w') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)

    def load_from_json(self, session_id: str) -> List[dict[str, str]]:
        """
        Load the chat history from a JSON file.

        :param session_id: str
            The session ID of the chat history to load.

        :return: List[Dict[str, str]]
            A list of dictionaries representing the chat history.

        :raises FileNotFoundError: If the chat history file does not exist.
        :raises ValueError: If the file contains invalid data (not a valid list of messages).
        """
        full_path = f'{self.folder_path}/{session_id}'
        if not self.is_file_exists(session_id):
            return []
        with open(full_path, 'r') as f:
            try:
                chat_history = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("The chat history file does not contain a valid list of messages.")
            if not isinstance(chat_history, list):
                raise ValueError("The chat history file does not contain a valid list of messages.")
            return chat_history
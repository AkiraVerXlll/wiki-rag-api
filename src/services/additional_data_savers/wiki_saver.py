import wikipediaapi

from src.services.additional_data_savers.base_additional_data_saver import IAdditionalDataSaver
from src.core.settings import USER_AGENT

class WikiSaver(IAdditionalDataSaver):

    def __init__(self, folder_path: str):
        """
        Initialize the WikiSaver with a specified folder path for saving articles.

        :param folder_path: str
            The directory path where the Wikipedia articles will be saved.
        """
        super().__init__(folder_path)
        self.wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT)

    def save(self, topic: str, document_id: str) -> str:
        """
        Save the content of a Wikipedia article to a text file.

        :param topic: str
            The title of the Wikipedia article to save.
        :param document_id: str
            The ID to use for naming the saved file.

        :return: str
            The full path to the saved text file.

        :raises ValueError: If the specified article does not exist on Wikipedia.
        """
        article = self.wiki.page(topic)
        if not article.exists():
            raise ValueError(f"Article {topic} does not exist.")
        full_path = f"{self.folder_path}/{document_id}.txt"
        with open(full_path, "w") as f:
            f.write(article.text)
        return full_path
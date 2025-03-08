import abc

class IAdditionalDataSaver(abc.ABC):
    """
    Abstract base class for saving additional data to a text file.
    """
    def __init__(self, folder_path: str):
        """
        :param folder_path: str
            The directory path where the articles will be saved.
        """
        self.folder_path = folder_path

    @abc.abstractmethod
    def save(self, topic: str, document_id: str) -> str:
        """
                Save the content to a text file.

                :param topic: str
                    The title of the article to save.
                :param document_id: str
                    The ID to use for naming the saved file.

                :return: str
                    The full path to the saved text file.
                """
        pass
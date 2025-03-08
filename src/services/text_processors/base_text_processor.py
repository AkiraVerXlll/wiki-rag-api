import abc

class ITextProcessor(abc.ABC):
    """
    Abstract base class for text processing tasks involving indexing and searching.
    """
    def __init__(self, folder_path: str):
        """
        :param folder_path: str
            The directory where FAISS indices are stored or loaded from.
        """
        self.folder_path = folder_path

    @abc.abstractmethod
    def index_exists(self, index: str) -> bool:
        """
                Check if an index with the specified name already exists.

                :param index: str
                    The name of the index to check for existence.

                :return: bool
                    True if the index exists, False otherwise.
                """
        pass

    @abc.abstractmethod
    def load_index(self, index: str):
        """
                Load an index from the specified file path and assign it to the vectorstore.

                :param index: str
                    The name of the index to load.
                """
        pass

    @abc.abstractmethod
    def create_index(self, text: str, index: str, chunk_size: int = 512, chunk_overlap: int = 50):
        """
                Create an index from the provided text and save it to the specified file path.

                :param text: str
                    The text to be indexed.
                :param index: str
                    The name under which the index will be saved.
                :param chunk_size: int, optional
                    The maximum size of each chunk (default is 512).
                :param chunk_overlap: int, optional
                    The number of overlapping characters between consecutive chunks (default is 50).
                """
        pass

    @abc.abstractmethod
    def search_mutual_information(self, query: str) -> str:
        """
                Search for similar content in the indexed text.
                Returns the most relevant information related to the query.

                :param query: str
                    The search query to find similar content for.

                :return: str
                    The most relevant information from the indexed text related to the query.
                """
        pass
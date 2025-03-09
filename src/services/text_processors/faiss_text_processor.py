from itertools import dropwhile

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from src.services.text_processors.base_text_processor import ITextProcessor
import os


class FaissTextProcessor(ITextProcessor):

    def __init__(self, folder_path: str, model: str = "text-embedding-3-large"):
        """
        Initialize the TextProcessor with an embedding model (OpenAIEmbeddings)
        and specify the folder path for storing and loading indices.

        :param folder_path: str
            The directory where FAISS indices are stored or loaded from.
        """
        super().__init__(folder_path)
        self.embedding_model = OpenAIEmbeddings(model=model)
        self.vectorstore = None

    def index_exists(self, faiss_index: str) -> bool:
        """
        Check if a FAISS index with the specified name already exists.

        :param faiss_index: str
            The name of the FAISS index to check for existence.

        :return: bool
            True if the index exists, False otherwise.
        """
        return os.path.exists(f'{self.folder_path}/{faiss_index}')

    def load_index(self, faiss_index: str):
        """
        Load a FAISS index from the specified file path and assign it to the vectorstore.

        :param faiss_index: str
            The name of the FAISS index to load.
        """
        self.vectorstore = FAISS.load_local(f'{self.folder_path}/{faiss_index}', self.embedding_model, allow_dangerous_deserialization=True)

    @staticmethod
    def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[Document]:
        """
        Split the input text into smaller chunks of specified size with an overlap between them.

        :param text: str
            The input text to be split into chunks.
        :param chunk_size: int
            The maximum number of characters in each chunk.
        :param chunk_overlap: int
            The number of overlapping characters between adjacent chunks.

        :return: List[Document]
            A list of Document objects, each representing a chunk of text.
        """
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(text)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents

    def create_index(self, text: str, faiss_index: str, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Create a FAISS index from the provided text and save it to the specified file path.

        :param text: str
            The text to be indexed.
        :param faiss_index: str
            The name under which the FAISS index will be saved.
        :param chunk_size: int, optional
            The maximum size of each chunk (default is 512).
        :param chunk_overlap: int, optional
            The number of overlapping characters between consecutive chunks (default is 50).
        """
        documents = self.split_text(text, chunk_size, chunk_overlap)
        self.vectorstore = FAISS.from_documents(documents, self.embedding_model)
        self.vectorstore.save_local(f'{self.folder_path}/{faiss_index}')

    def search_mutual_information(self, query: str, top_k: int = 1) -> str:
        """
        Search for the most similar text chunks to the provided query using the FAISS index.

        :param query: str
            The search query to find similar text chunks.
        :param top_k: int, optional
            The number of top similar results to return (default is 1).

        :return: str
            A string representing the most similar text chunks concatenated together.

        :raises ValueError: If the FAISS index has not been loaded or created.
        """
        if not self.vectorstore:
            raise ValueError("FAISS index has not been downloaded or created!")

        result = self.vectorstore.similarity_search(query, k=top_k)
        result = " ".join([doc.page_content for doc in result])
        return result
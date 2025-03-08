from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from typing import List
from src.settings import INDICES_PATH
import os


class TextProcessor:
    def __init__(self, indices_path: str = INDICES_PATH):
        """
        Initializes the TextProcessor with an embedding model (OpenAIEmbeddings)
        and sets the indices folder path.

        Args:
            indices_path (str): The path to the folder where the indices are stored.
        """
        self.embedding_model = OpenAIEmbeddings()
        self.index_path = indices_path
        self.vectorstore = None

    def index_exists(self, faiss_index: str) -> bool:
        """
        Checks if a FAISS index with the given name exists.

        Args:
            faiss_index (str): The name of the FAISS index to check.

        Returns:
            bool: True if the index exists, False otherwise.
        """
        return os.path.exists(f'{self.index_path}/{faiss_index}')

    def load_faiss_index(self, faiss_index: str):
        """
        Loads a FAISS index from the specified path and sets it to the vectorstore.

        Args:
            faiss_index (str): The name of the FAISS index to load.
        """
        self.vectorstore = FAISS.load_local(f'{self.index_path}/{faiss_index}', self.embedding_model)

    @staticmethod
    def split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[Document]:
        """
        Splits the input text into chunks of specified size with some overlap between them.

        Args:
            text (str): The text to split.

        Returns:
            List[Document]: A list of Document objects representing the text chunks.
        """
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(text)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents

    def create_faiss_index(self, text: str, faiss_index: str, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Creates a FAISS index from the input text and saves it to the specified path.

        Args:
            text (str): The text to create the index from.
            faiss_index (str): The name to save the FAISS index under.
            chunk_size (int): The maximum size of each chunk (default is 512).
            chunk_overlap (int): The number of overlapping characters between consecutive chunks (default is 50).
        """
        documents = self.split_text(text, chunk_size, chunk_overlap)
        self.vectorstore = FAISS.from_documents(documents, self.embedding_model)
        self.vectorstore.save_local(f'{self.index_path}/{faiss_index}')

    def search_similar_chunks(self, query: str, top_k: int = 1) -> List[Document]:
        """
        Searches for the most similar text chunks to the given query using the loaded FAISS index.

        Args:
            query (str): The search query to find similar chunks for.
            top_k (int): The number of top similar results to return (default is 1).

        Returns:
            List[Document]: A list of Document objects representing the most similar text chunks.

        Raises:
            ValueError: If the FAISS index is not loaded or created.
        """
        if not self.vectorstore:
            raise ValueError("FAISS index has not been downloaded or created!")

        results = self.vectorstore.similarity_search(query, k=top_k)
        return results
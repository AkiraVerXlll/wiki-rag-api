from celery import Celery
import os

from src.settings import REDIS_URL
from src.services.additional_data_savers.base_additional_data_saver import IAdditionalDataSaver
from src.services.text_processors.base_text_processor import ITextProcessor
from src.services.text_processors.faiss_text_processor import FaissTextProcessor
from src.services.chat_history_parser import ChatHistoryParser
from src.services.prompt_builder import PromptBuilder
from src.settings import DOCUMENTS_PATH, OPENAI_API_TOKEN, MODEL
import openai

celery_app = Celery('worker',
                    broker=REDIS_URL,
                    backend=REDIS_URL)

def get_task_status(task_id: str) -> str:
    """
    Retrieves the status of a background task based on its task ID.

    :param task_id: str
        The unique ID of the task to check the status for.

    :return: str
        The current status of the task (e.g., 'pending', 'running', 'finished', 'failed').

    :raises Exception:
        If there is an issue with the task ID or the task cannot be found.
    """
    task = celery_app.AsyncResult(task_id)
    return task.status

def document_exists(document_id: str) -> bool:
    """
    Checks if a document with the given document_id exists in the specified path.

    :param document_id: str
        The ID of the document to check.

    :return: bool
        True if the document exists, False otherwise.
    """
    return os.path.exists(f"{DOCUMENTS_PATH}/{document_id}.txt")

@celery_app.task()
def retrieve_wikipedia_content(topic: str, document_id: str, saver_type: str, additional_data_path: str):
    """
    Retrieves a Wikipedia article by its topic and saves it to the specified path.
    If the document already exists at the specified path, raises an exception.

    :param topic: str
        The topic of the Wikipedia article to retrieve.
    :param document_id: str
        The ID used to name the saved file. This will be used as the file name for the saved document.
    :param saver_type: str
        The name of the class used to save the article (e.g., 'WikiSaver').
    :param additional_data_path: str
        The path to the location where the article will be saved. This is used by the saver to store the document.

    :raises ValueError:
        If the document with the given ID already exists at the specified path.
    :raises ValueError:
        If the provided saver type is invalid or not found.
    """
    saver_class = globals()[saver_type]
    if saver_class is None:
        raise ValueError(f"Invalid saver type: {saver_type}")
    saver = saver_class(additional_data_path)
    if document_exists(document_id):
        raise ValueError(f"Document with ID {document_id} already exists.")
    saver.save(topic, document_id)

def similar_search(query: str, document_id: str, text_parser: FaissTextProcessor) -> str:
    """
    Searches for similar content in a document.
    Returns the most relevant information related to the query.

    :param query: str
        The search query to find similar content for.
    :param document_id: str
        The ID of the document to search within.
    :param text_parser: TextProcessor
        An instance of TextProcessor used for creating and querying the FAISS index.

    :return: str
        The most relevant information from the document related to the query.

    :raises ValueError:
        If the document does not exist and the FAISS index is not yet created.
    """
    if text_parser.index_exists(document_id):
        text_parser.load_index(document_id)
        return text_parser.search_mutual_information(query)

    if not document_exists(document_id):
        raise ValueError(f"Document with ID {document_id} does not exist.")
    with open(f"{DOCUMENTS_PATH}/{document_id}.txt", "r") as f:
        text = f.read()

    text_parser.create_index(document_id, text)
    return text_parser.search_mutual_information(query)

def get_chat_response(session_id: str,
                      document_id: str,
                      inputs: str,
                      history_parser: ChatHistoryParser,
                      text_parser: FaissTextProcessor) -> str:
    """
        Retrieves a chat response from the OpenAI API based on the session history and input.
        It also integrates RAG by using relevant document information.

        :param session_id: str
            The session ID to load the chat history.
        :param document_id: str
            The document ID to fetch relevant information from.
        :param inputs: str
            The user input for the current chat.
        :param history_parser: ChatHistoryParser
            An instance of ChatHistoryParser to load and save the chat history.
        :param text_parser: TextProcessor
            An instance of TextProcessor to handle document indexing and searching.

        :return: str
            The generated response from the OpenAI model.

        :raises ValueError:
            If an error occurs while interacting with the OpenAI API.
        """
    try:
        chat_history = history_parser.load_from_json(session_id)
    except:
        chat_history = []
    finally:
        rag_info = similar_search(inputs, document_id, text_parser)
        prompt_builder = PromptBuilder()
        chat_history = prompt_builder.build_prompt(chat_history, inputs, rag_info)
        try:
            openai.api_key = OPENAI_API_TOKEN
            response = openai.Completion.create(
                model = MODEL,
                messages = chat_history
            )
        except Exception as e:
            raise ValueError(f"Failed to generate response: {str(e)}")
        response = response.choices[0].text.strip()
        chat_history.append({"role": "assistant", "content": response})
        history_parser.save_to_json(chat_history, session_id)
        return response


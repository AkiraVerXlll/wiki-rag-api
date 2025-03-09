import os
from typing import Optional

from celery import Celery
from loguru import logger
from openai import OpenAI

from src.core.exceptions import (
    DocumentNotFoundError,
    SessionNotFoundError,
    OpenAIError,
    TaskNotFoundError,
    WikipediaError,
    ValidationError
)
from src.core.settings import REDIS_URL, DOCUMENTS_PATH, OPENAI_API_TOKEN, MODEL
from src.services.text_processors import ITextProcessor
from src.services.chat_history_parser import ChatHistoryParser
from src.services.prompt_builder import PromptBuilder
import src.services.additional_data_savers as additional_data_savers

celery_app = Celery('tasks', broker=REDIS_URL)

def get_task_status(task_id: str) -> str:
    """
    Retrieves the status of a background task based on its task ID.

    :param task_id: str
        The unique ID of the task to check the status for.

    :return: str
        The current status of the task (e.g., 'pending', 'running', 'finished', 'failed').

    :raises TaskNotFoundError:
        If the task with the given ID cannot be found.
    """
    task = celery_app.AsyncResult(task_id)
    if not task:
        raise TaskNotFoundError(task_id)
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

    :raises ValidationError:
        If the document with the given ID already exists at the specified path.
    :raises ValidationError:
        If the provided saver type is invalid or not found.
    :raises WikipediaError:
        If there's an error fetching data from Wikipedia.
    """
    try:
        saver_class = getattr(additional_data_savers, saver_type)
        if saver_class is None:
            raise ValidationError(f"Invalid saver type: {saver_type}")
        
        saver = saver_class(additional_data_path)
        if document_exists(document_id):
            raise ValidationError(f"Document with ID {document_id} already exists.")
        
        saver.save(topic, document_id)
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise WikipediaError(f"Failed to retrieve Wikipedia content: {str(e)}")

def similar_search(query: str, document_id: str, text_parser: ITextProcessor) -> str:
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

    :raises DocumentNotFoundError:
        If the document does not exist and the FAISS index is not yet created.
    """
    try:
        if text_parser.index_exists(document_id):
            text_parser.load_index(document_id)
            return text_parser.search_mutual_information(query)

        if not document_exists(document_id):
            raise DocumentNotFoundError(document_id)
            
        with open(f"{DOCUMENTS_PATH}/{document_id}.txt", "r") as f:
            text = f.read()

        text_parser.create_index(text, document_id)
        return text_parser.search_mutual_information(query)
    except Exception as e:
        if isinstance(e, DocumentNotFoundError):
            raise
        logger.error(f"Error in similar_search: {str(e)}")
        raise ValidationError("Failed to search document", details={"error": str(e)})

def get_chat_response(session_id: str,
                      document_id: str,
                      inputs: str,
                      history_parser: ChatHistoryParser,
                      text_parser: ITextProcessor) -> str:
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

    :raises SessionNotFoundError:
        If the chat session history cannot be found.
    :raises DocumentNotFoundError:
        If the requested document cannot be found.
    :raises OpenAIError:
        If an error occurs while interacting with the OpenAI API.
    """
    try:
        try:
            chat_history = history_parser.load_from_json(session_id)
        except FileNotFoundError:
            raise SessionNotFoundError(session_id)
        
        rag_info = similar_search(inputs, document_id, text_parser)
        prompt_builder = PromptBuilder()
        chat_history = prompt_builder.build_prompt(chat_history, inputs, rag_info)
        
        try:
            client = OpenAI(api_key=OPENAI_API_TOKEN)
            response = client.chat.completions.create(
                model=MODEL,
                messages=chat_history
            )
        except Exception as e:
            raise OpenAIError(f"Failed to generate response: {str(e)}")
        
        response = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": response})
        history_parser.save_to_json(chat_history, session_id)
        return response
        
    except Exception as e:
        if isinstance(e, (SessionNotFoundError, DocumentNotFoundError, OpenAIError)):
            raise
        logger.error(f"Unexpected error in get_chat_response: {str(e)}")
        raise ValidationError("Failed to process chat request", details={"error": str(e)})


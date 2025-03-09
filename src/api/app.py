from celery.result import AsyncResult
from fastapi import FastAPI
from loguru import logger

from src.scemas.inputs import ProcessInputs, ChatInputs
from src.api.dependencies import AdditionalDataSaver, HistoryParser, TextProcessor
from src.core.worker import celery_app, retrieve_wikipedia_content, get_chat_response
from src.api.middleware import error_handler_middleware
from src.core.logging import setup_fastapi_logging
from src.core.exceptions import (
    TaskNotFoundError,
    DocumentNotFoundError,
    OpenAIError,
    ValidationError
)

setup_fastapi_logging()

app = FastAPI()

app.middleware("http")(error_handler_middleware)

@app.post("/api/v1/process")
def process(inputs: ProcessInputs, additional_data_saver: AdditionalDataSaver):
    """
    Accept textual requests and launch a background task to gather textual information from Wikipedia.
    It should receive the user's request and start a background task for processing. After starting a task,
    it should return an identifier for the task.

    The results should be stored as a file `{document_id}.txt` in the `data/documents` directory.

    Examples of a valid user request:
    - Kyiv
    - Isaac Newton
    - Spider-man

    :return: task_id of the background task that was started
    :raises ValidationError: If the input validation fails
    :raises WikipediaError: If there's an error fetching data from Wikipedia
    """
    try:
        logger.info(f"Processing request for topic: {inputs.topic}")
        path = additional_data_saver.folder_path
        class_name = type(additional_data_saver).__name__
        task = retrieve_wikipedia_content.delay(inputs.topic, inputs.document_id, class_name, path)
        logger.info(f"Started background task with ID: {task.id}")
        return {"task_id": task.id}, 200
    except Exception as e:
        logger.error(f"Error processing Wikipedia request: {str(e)}")
        raise ValidationError("Failed to process Wikipedia request", details={"error": str(e)})


@app.get("/api/v1/status/{task_id}")
def status(task_id: str):
    """
    Check the status of the background task. It should receive a task_id path parameter and return the status of the task.
    The task can have four possible statuses: pending, running, finished, or failed.

    :param task_id: str
        The ID of the task to check

    :return: status of the background task (pending, running, finished, or failed)
    :raises TaskNotFoundError: If the task with the given ID is not found
    """
    logger.info(f"Checking status for task: {task_id}")
    task = AsyncResult(task_id, app=celery_app)
    if not task:
        raise TaskNotFoundError(task_id)
    return {"status": task.status}, 200


@app.post("/api/v1/chat")
def chat(inputs: ChatInputs, history_parser: HistoryParser, text_processor: TextProcessor):
    """
    Endpoint for interaction with СhatGPT. The document with `document_id` identifier should be inserted
    into СhatGPT prompt, so the user will be able to chat about specific topic.

    The session history should be persistent and stored as `{session_id}.json` in the `data/sessions` directory
    in a JSON format. So, each time you call the `chat` endpoint, session history will be pulled from the file and used
    for generation.

    :param inputs: ChatInputs
        Contains:
        - session_id: str - Session identifier to keep track of the conversation
        - document_id: str - Identifier of a textual document to insert into prompt
        - text: str - User input text
    :param history_parser: HistoryParser
        Component for loading and saving chat history from/to JSON files
    :param text_processor: TextProcessor
        Component for processing and searching text in documents

    :return: dict
        A dictionary containing:
        - response: str - The generated response from ChatGPT
        - status: int - HTTP status code (200 for success)

    :raises DocumentNotFoundError: If the requested document is not found
    :raises OpenAIError: If there's an error with the OpenAI API
    :raises ValidationError: If the input validation fails
    """
    logger.info(f"Processing chat request for session: {inputs.session_id}")
    try:
        response = get_chat_response(inputs.session_id, inputs.document_id,
                                   inputs.text, history_parser, text_processor)
        logger.info(f"Successfully generated response for session: {inputs.session_id}")
        return {"response": response}, 200
    except (DocumentNotFoundError, OpenAIError) as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise ValidationError("Failed to process chat request", details={"error": str(e)})


@app.get("/-/healthy/")
def healthy():
    return {}, 200

from celery.result import AsyncResult
from fastapi import FastAPI
from sqlalchemy.orm import class_mapper

from src.scemas.inputs import ProcessInputs, ChatInputs
from src.dependencies import AdditionalDataSaver, HistoryParser, TextProcessor
from src.worker import celery_app, retrieve_wikipedia_content, get_chat_response

app = FastAPI()


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
    """
    path = additional_data_saver.folder_path
    class_name = type(additional_data_saver).__name__
    task = retrieve_wikipedia_content.delay(inputs.topic, inputs.document_id, class_name, path)
    return {"task_id": task.id}, 200


@app.get("/api/v1/status/{task_id}")
def status(task_id: str):
    """
    Check the status of the background task. It should receive a task_id path parameter and return the status of the task.
    The task can have four possible statuses: pending, running, finished, or failed.

    :param task_id: str

    :return: status of the background task (pending, running, finished, or failed)
    """
    task = AsyncResult(task_id, app=celery_app)
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
        1. session_id – session identifier to keep track of the conversation.
        2. document_id - identified of a textual document to insert into prompt.
        2. text – user input text

    :return: bot response
    """
    response = get_chat_response(inputs.session_id, inputs.document_id,
                                 inputs.text, history_parser, text_processor)
    return {"response": response}, 200


@app.get("/-/healthy/")
def healthy():
    return {}, 200

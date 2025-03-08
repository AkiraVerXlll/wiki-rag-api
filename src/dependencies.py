from itertools import dropwhile
from typing import Annotated

from fastapi import Depends

from src.services.additional_data_savers.base_additional_data_saver import IAdditionalDataSaver
from src.services.additional_data_savers.wiki_saver import WikiSaver
from src.services.chat_history_parser import ChatHistoryParser
from src.services.text_processors.base_text_processor import ITextProcessor
from src.services.text_processors.faiss_text_processor import FaissTextProcessor
from src.settings import INDICES_PATH, DOCUMENTS_PATH, SESSIONS_PATH


def get_faiss_text_processor() -> FaissTextProcessor:
    return FaissTextProcessor(INDICES_PATH)

def get_wiki_saver() -> WikiSaver:
    return WikiSaver(DOCUMENTS_PATH)

def get_chat_history_parser() -> ChatHistoryParser:
    return ChatHistoryParser(SESSIONS_PATH)

TextProcessor = Annotated[FaissTextProcessor, Depends(get_faiss_text_processor)]
AdditionalDataSaver = Annotated[IAdditionalDataSaver, Depends(get_wiki_saver)]
HistoryParser = Annotated[ChatHistoryParser, Depends(get_chat_history_parser)]
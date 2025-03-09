from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProcessInputs(BaseModel):
    """
    Input model for processing Wikipedia requests.
    
    :param topic: The topic to search for on Wikipedia
    :param document_id: Unique identifier for the document
    """
    topic: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Topic to search for on Wikipedia"
    )
    document_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern="^[a-zA-Z0-9-_]+$",
        description="Unique identifier for the document"
    )

class ChatInputs(BaseModel):
    """
    Input model for chat requests.
    
    :param session_id: Unique identifier for the chat session
    :param document_id: Identifier of the document to chat about
    :param text: User's input text
    """
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern="^[a-zA-Z0-9-_]+$",
        description="Unique identifier for the chat session"
    )
    document_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern="^[a-zA-Z0-9-_]+$",
        description="Identifier of the document to chat about"
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's input text"
    )

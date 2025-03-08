from pydantic import BaseModel

class ProcessInputs(BaseModel):
    topic: str
    document_id: str


class ChatInputs(BaseModel):
    session_id: str
    document_id: str
    text: str

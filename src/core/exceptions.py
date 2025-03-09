from typing import Any, Dict, Optional

class AppException(Exception):
    """
    Base exception for all application errors.

    :param message: 
        The error message
    :param status_code: 
        HTTP status code (default: 500)
    :param details: 
        Additional error details (default: None)
    """
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DocumentNotFoundError(AppException):
    """
    Raised when a requested document is not found.

    :param document_id: 
        The ID of the document that was not found
    """
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with ID {document_id} not found",
            status_code=404
        )

class SessionNotFoundError(AppException):
    """
    Raised when a requested chat session is not found.

    :param session_id: 
        The ID of the session that was not found
    """
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Chat session with ID {session_id} not found",
            status_code=404
        )

class OpenAIError(AppException):
    """
    Raised when there's an error with OpenAI API.

    :param message: 
        The error message
    :param details: 
        Additional error details (default: None)
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )

class WikipediaError(AppException):
    """
    Raised when there's an error fetching data from Wikipedia.

    :param message: 
        The error message
    :param details: 
        Additional error details (default: None)
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )

class ValidationError(AppException):
    """
    Raised when there's a validation error in the input data.

    :param message: 
        The error message
    :param details: 
        Additional error details (default: None)
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )

class TaskNotFoundError(AppException):
    """
    Raised when a requested Celery task is not found.

    :param task_id: 
        The ID of the task that was not found
    """
    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task with ID {task_id} not found",
            status_code=404
        ) 
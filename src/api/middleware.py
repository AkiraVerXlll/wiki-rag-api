from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.exceptions import AppException

async def error_handler_middleware(request: Request, call_next):
    """
    Middleware to handle exceptions and return appropriate responses.

    :param request: 
        The incoming request
    :param call_next: 
        The next middleware/handler in the chain
    :return: Response: 
        The response to send back to the client
    """
    try:
        return await call_next(request)
    except AppException as e:
        logger.error(f"Application error: {e.message}", extra=e.details)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.exception("Unexpected error occurred")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(e)
            }
        ) 
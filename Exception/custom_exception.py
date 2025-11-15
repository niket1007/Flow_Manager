from fastapi import Request
from fastapi.responses import JSONResponse
from Models.common_models import ErrorResponseModel

class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
    

def custom_exception_handler(req: Request, exc: CustomException):
    return JSONResponse(
        content=ErrorResponseModel(message=exc.message).model_dump(), status_code=exc.status_code)
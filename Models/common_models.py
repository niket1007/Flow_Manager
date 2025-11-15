from pydantic import BaseModel, Field
from typing import Annotated

class ErrorResponseModel(BaseModel):
    message: Annotated[str,Field(description="Error message")]
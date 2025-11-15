from pydantic import BaseModel, Field
from typing import Annotated


class TaskModel(BaseModel):
    name: Annotated[str, Field(description="Task function name")]
    description: Annotated[str, Field(description="Task description")]

class ConditionModel(BaseModel):
    name: Annotated[str, Field(description="Condition name")]
    description: Annotated[str, Field(description="Condition description")]
    source_task: Annotated[str, Field(description="Task name")]
    outcome: Annotated[str, Field(description="Task expected outcome")]
    target_task_success: Annotated[str, Field(description="Next action if task executes successfully")]
    target_task_failure: Annotated[str, Field(description="Next action if task fails")]

class FlowModel(BaseModel):
    id: Annotated[str,Field(description="Flow id")]
    name: Annotated[str,Field(description="Flow name")]
    start_task: Annotated[str,Field(description="Flow starting function")]
    tasks: Annotated[list[TaskModel], Field(description="Task details")]
    conditions: Annotated[list[ConditionModel], Field(description="Conditions")]

class RequestPayload(BaseModel):
    flow: Annotated[FlowModel, Field(description="Flow detail")]

class ResponsePayload(BaseModel):
    id: Annotated[str,Field(description="Flow id")]
    name: Annotated[str,Field(description="Flow name")]
    report: Annotated[list[str], Field(default=[], description="Flow execution report")]

class TaskInformationResponsePayload(BaseModel):
    name: Annotated[str, Field(description="Task function name")]
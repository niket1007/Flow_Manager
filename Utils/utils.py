from Models.flow_models import TaskInformationResponsePayload

def transformToTfResponse(tasks: dict[str, dict]) -> list[TaskInformationResponsePayload]:
    result = []
    for task in tasks:
        result.append(TaskInformationResponsePayload(name=task))
    return result
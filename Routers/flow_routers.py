from fastapi import APIRouter
from Logger.logger import log
from Flow.flow import FlowManager
from Flow.tasks import TaskManager
from Models.flow_models import TaskInformationResponsePayload, RequestPayload, ResponsePayload
from Models.common_models import ErrorResponseModel
from Utils.utils import transformToTfResponse
from Exception.custom_exception import CustomException

router = APIRouter(prefix="/flows", tags=["Flow"])

responses = {
    400: {"model": ErrorResponseModel},
    500: {"model": ErrorResponseModel}
}

@router.get(path="/tasks",
            status_code=200,
            response_model=list[TaskInformationResponsePayload])
async def get_task_informations():
    log.info("get_task_infomations started")
    try:
        task = TaskManager()
        task_dict = task.get_tasks_information()
        result = transformToTfResponse(task_dict)
        return result
    except CustomException:
        raise  
    except Exception as e:
        log.error(f"Unexpected error in fetching task details: {e}")
        raise CustomException("Internal server error during fetching task details", 500)



@router.post(path="/execute", 
             status_code=201,
             responses=responses,
             response_model=ResponsePayload)
async def execute_tasks(req_body: RequestPayload):
    try:
        flow = FlowManager(user_flow=req_body)
        report = flow.execute_flow()
        log.info(f"execute_tasks completed for flow_id: {req_body.flow.id}")
        return report
    except CustomException:
        raise  
    except Exception as e:
        log.error(f"Unexpected error in flow execution: {e}")
        raise CustomException("Internal server error during flow execution", 500)

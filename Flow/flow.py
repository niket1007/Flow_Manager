from Flow.tasks import TaskManager
from Models.flow_models import RequestPayload, ResponsePayload
from Exception.custom_exception import CustomException
from Logger.logger import log

class FlowManager:
    def __init__(self, user_flow: RequestPayload):
        self.user_flow = user_flow
        self.task_manager = TaskManager()
        self.execution_dict: dict = {}


    def start_execution(self):
        log.info("start_execution called")
        task = self.user_flow.flow.start_task
        visited_tasks = set()
        
        while task != "end":
            log.debug(f"Invoked task: '{task}'")
            if task in visited_tasks:
                raise CustomException(f"Cycle detected: task '{task}' visited multiple times", 500)
            visited_tasks.add(task)
            task_func = self.execution_dict[task]["execute"]
            try:
                result = task_func()
            except Exception as e:
                log.error(f"Task '{task}' raised exception: {e}")
                raise CustomException(message=f"Task '{task}' raised exception: {e}", status_code=500)

            condition = self.execution_dict[task]["condition"]
            if len(condition) != 0:
                outcome = condition["outcome"]

                log.debug(f"Task Result: {result} and Outcome: {outcome}")

                if result == outcome:
                    self.execution_dict[task]["report"] = f"'{task}' executed successfully."
                    task = condition["success"]          
                else:  
                    self.execution_dict[task]["report"] = f"'{task}' failed."
                    task = condition["failure"]
            else:
                log.debug(f"Condition not present. Considering '{task}' as last task.")
                self.execution_dict[task]["report"] = f"'{task}' is the last task."
                task = "end"

        log.info("start_execution ended: task execution completed")

    def prepare_report(self) -> ResponsePayload:
        log.info("prepare_report called")
        response = ResponsePayload(
            id=self.user_flow.flow.id,
            name=self.user_flow.flow.name
        )

        final_report = []
        for task in self.execution_dict:
            final_report .append(f"{self.execution_dict[task].get("report", "")}")
        
        log.debug(f"Final report: {final_report}")
        response.report = final_report
        return response

    def execute_flow(self) -> ResponsePayload:
        log.info("execution_flow called")
        task_dictionary = self.task_manager.get_tasks_information()

        if self.user_flow.flow.start_task not in task_dictionary:
            raise CustomException(
                    message=f"Start Task '{self.user_flow.flow.start_task}' does not exist", 
                    status_code=400)

        for task in self.user_flow.flow.tasks:
            if task.name not in task_dictionary:
                raise CustomException(
                    message=f"Task name '{task.name}' does not exist", status_code=400)
            self.execution_dict[task.name] = {
                "condition": {}, "report":"", "execute": task_dictionary[task.name]}
    
        for condition in self.user_flow.flow.conditions:
            if condition.source_task not in task_dictionary:
                raise CustomException(
                    message=f"Condition source task '{condition.source_task}' does not exist", status_code=400)
            elif (condition.target_task_success != "end" 
                  and condition.target_task_success not in task_dictionary):
                raise CustomException(
                    message=f"Condition target success task '{condition.target_task_success}' does not exist", status_code=400)
            elif (condition.target_task_failure != "end" 
                  and condition.target_task_failure not in task_dictionary):
                raise CustomException(
                    message=f"Condition target failure task '{condition.target_task_failure}' does not exist", status_code=400)
            
            self.execution_dict[condition.source_task]["condition"] = {
                "outcome": condition.outcome, 
                "success": condition.target_task_success, 
                "failure": condition.target_task_failure}

        log.debug(f"Execution dictionary {self.execution_dict}")

        self.start_execution()
        result = self.prepare_report()
        return result

            

            
        
            
            



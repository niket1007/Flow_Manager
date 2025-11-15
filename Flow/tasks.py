from Logger.logger import log

class TaskManager:
    
    def __init__(self):
        self.task_dict = {
            "task1": self.task1,
            "task2": self.task2,
            "task3": self.task3
        }

    def get_tasks_information(self) -> dict:
        log.info("get_tasks_information called")
        return self.task_dict

    def task1(self) -> str:
        log.info("task1 called")
        return "success"
    
    def task2(self) -> str:
        log.info("task2 called")
        return "success"
    
    def task3(self) -> str:
        log.info("task3 called")
        return "success"

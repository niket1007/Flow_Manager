# Flow Manager Service

A Python-based microservice built with [FastAPI](https://fastapi.tiangolo.com/) to execute sequential task flows with conditional logic.

This service allows you to define complex workflows in a JSON format, where each task's execution and outcome (`"success"` or `"failure"`) determines the next step in the flow.

## Features

* **Dynamic Flow Execution:** Run complex, sequential task flows defined by a JSON input.
* **Conditional Logic:** Evaluate the string result of each task (e.g., `"success"`, `"failure"`) to determine the next step, whether it's proceeding to another task or ending the flow.
* **Robust Validation:** All incoming flow definitions are validated before execution. The service checks that the `start_task`, all `tasks`, and all conditional task names (source, success, failure) are valid and registered in the `TaskManager`.
* **Cycle Detection:** Automatically detects and prevents infinite loops (cycles) in the flow, raising a 500 error if a task is visited twice.
* **Task-Level Error Handling:** Any exception raised *within* an individual task (e.g., a database connection failure) is caught, logged, and will immediately halt the flow, returning a 500 error.
* **Centralised Error Handling:** Uses a custom exception class (`CustomException`) and a FastAPI handler to return clear, standardised JSON error messages for both bad requests (400) and server errors (500).

## Design Explained

This section answers the core design questions from the project brief.

### 1. How do the tasks depend on one another?

Task dependencies are not hardcoded. They are dynamically defined by the **`conditions` array** in the JSON payload.

Each object in the `conditions` array links a `source_task` to a `target_task_success` and a `target_task_failure`. The `FlowManager` uses this information to build an `execution_dict` at runtime, which maps out the exact execution path and dependencies for that specific flow.

### 2. How is the success or failure of a task evaluated?

The evaluation is a direct string comparison:

1.  **Task Return Value:** Each task function (e.g., `task1`, `task2`) is defined to return a simple string, such as `"success"`, upon completion.
2.  **Condition Outcome:** The `conditions` array specifies the *expected* string result for that task in its `outcome` field (e.g., `"outcome": "success"`).
3.  **Evaluation:** The `FlowManager` compares the actual string returned by the task (`result`) against the `outcome` string from the condition.

### 3. What happens if a task fails or succeeds?

The flow proceeds based on the result of the string comparison:

* **If the task's result *matches* the expected `outcome`** (a "success"): The `FlowManager` updates the next task to be the one specified in the `target_task_success` field.
* **If the task's result *does not match* the expected `outcome`** (a "failure"): The `FlowManager` updates the next task to be the one specified in the `target_task_failure` field.

If this new task value is `"end"`, the flow's `while` loop terminates, and the execution is complete.

## Project Structure
```
Flow_Manager/
├── Exception/
│   └── custom_exception.py   # Custom exception class and handler
├── Flow/
│   ├── flow.py               # Core FlowManager logic (validation, execution)
│   └── tasks.py              # TaskManager and task definitions
├── Logger/
│   └── logger.py             # Logging configuration
├── Models/
│   ├── common_models.py      # Error response model
│   └── flow_models.py        # Pydantic models for API requests/responses
├── Routers/
│   └── flow_routers.py       # API endpoint definitions (FastAPI)
├── Utils/
│   └── utils.py              # Helper functions
├── main.py                   # FastAPI app entry point
├── main.py                   # Environment File [Standard: Never commit this file in code but did for this assignment]
└── README.md                 # This file
```

## How to Run

1.  **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd Flow_Manager
    ```

2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    
3.  **Run the service:**
    From the directory *containing* the `Flow_Manager` folder:
    ```sh
    uvicorn Flow_Manager.main:app --reload
    ```
    The service will be running at `http://127.0.0.1:8000`.

## API Endpoints

### 1. Get Available Tasks

Retrieves a list of all available task functions registered in the `TaskManager`.

* **Endpoint:** `GET /flows/tasks`
* **Success Response (200 OK):**
    ```json
    [
      {
        "name": "task1"
      },
      {
        "name": "task2"
      },
      {
        "name": "task3"
      }
    ]
    ```

### 2. Execute a Flow

Executes a task flow based on the provided JSON definition.

* **Endpoint:** `POST /flows/execute`
* **Request Body:**
    ```json
    {
      "flow": {
        "id": "flow123",
        "name": "Data processing flow",
        "start_task": "task1",
        "tasks": [
          {
            "name": "task1",
            "description": "Fetch data"
          },
          {
            "name": "task2",
            "description": "Process data"
          },
          {
            "name": "task3",
            "description": "Store data"
          }
        ],
        "conditions": [
          {
            "name": "condition_task1_result",
            "description": "Evaluate task1. If successful, proceed to task2; otherwise, end.",
            "source_task": "task1",
            "outcome": "success",
            "target_task_success": "task2",
            "target_task_failure": "end"
          },
          {
            "name": "condition_task2_result",
            "description": "Evaluate task2. If successful, proceed to task3; otherwise, end.",
            "source_task": "task2",
            "outcome": "success",
            "target_task_success": "task3",
            "target_task_failure": "end"
          }
        ]
      }
    }
    ```

* **Success Response (201 Created):**
    Returns a `ResponsePayload` with a list of execution reports.
    ```json
    {
      "id": "flow123",
      "name": "Data processing flow",
      "report": [
        "'task1' executed successfully.",
        "'task2' executed successfully.",
        "'task3' is the last task."
      ]
    }
    ```

* **Error Response (400 Bad Request):**
    This occurs if the flow definition is invalid (e.g., a task name doesn't exist).
    ```json
    {
      "message": "Task name 'task_does_not_exist' does not exist"
    }
    ```

* **Error Response (500 Internal Server Error):**
    This occurs if a cycle is detected or an individual task crashes.
    ```json
    {
      "message": "Cycle detected: task 'task1' visited multiple times"
    }
    ```
    *or*
    ```json
    {
      "message": "Task 'task2' raised exception: Something bad happened"
    }
    ```

## How to Extend (Add New Tasks)

To add new tasks that the `FlowManager` can execute:

1.  Open `Flow_Manager/Flow/tasks.py`.
2.  Define your new task as a method within the `TaskManager` class. It must return a string (e.g., `"success"`, `"failure"`) that can be evaluated by the conditions.
    ```python
    def my_new_task(self) -> str:
        log.info("my_new_task called")
        # ... do real work ...
        if ...:
            return "success"
        else:
            return "failure"
    ```
3.  Register your new task function in the `self.task_dict` within the `__init__` method.
    ```python
    class TaskManager:
        def __init__(self):
            self.task_dict = {
                "task1": self.task1,
                "task2": self.task2,
                "task3": self.task3,
                "my_new_task_name": self.my_new_task  # Add your new task here
            }
    ```
4.  Restart the server. Your new task `"my_new_task_name"` will now be available to the `GET /flows/tasks` endpoint and can be used in flow definitions.

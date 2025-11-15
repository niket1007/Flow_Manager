from fastapi import FastAPI
from Routers.flow_routers import router as flow_routers
from Exception.custom_exception import CustomException, custom_exception_handler
from decouple import config

app = FastAPI(
    version=config("api_version", cast=str),
    title="Flow Manager Service")

app.include_router(flow_routers)
app.add_exception_handler(CustomException, custom_exception_handler)
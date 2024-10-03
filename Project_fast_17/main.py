from fastapi import FastAPI
from routers.task import router as task_router
from routers.user import router as user_router
import uvicorn

upp = FastAPI()


@upp.get("/")
async def welcome():
    return {"message": "Welcome to Taskmanager"}


upp.include_router(user_router)
upp.include_router(task_router)


if __name__ == "__main__":
    uvicorn.run("main:upp",  reload=True)



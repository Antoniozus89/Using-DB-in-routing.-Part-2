from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated
from backend.db_depends import get_db
from models.task import Task
from schemas import CreateTask, UpdateTask
from models.user import User

router = APIRouter(prefix="/task", tags=["task"])



@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks



@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    return task



@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, create_task: CreateTask):
    user_stmt = select(User).where(User.id == user_id)
    user = db.execute(user_stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    new_task = Task(
        title=create_task.title,
        content=create_task.content,
        priority=create_task.priority,
        completed=False,
        slug=slugify(create_task.title),
        user_id=user_id
    )

    db.add(new_task)
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    # db.execute(insert(Task).values(
    #     title=create_task.title,
    #     content=create_task.content,
    #     priority=create_task.priority,
    #     completed=False,
    #     slug=slugify(create_task.title),
    #     user_id=user_id,
    # ))

    db.commit()


    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update/{task_id}")
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, update_task: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )


    db.execute(update(Task).where(Task.id == task_id).values(
        title=update_task.title,
        content=update_task.content,
        priority=update_task.priority,
        completed=update_task.completed
    ))

    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful!'
    }


@router.delete("/delete/{task_id}")
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )

    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task delete is successful!'
    }
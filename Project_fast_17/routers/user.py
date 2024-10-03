from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, delete, update
from models.user import User
from models.task import Task
from backend.db_depends import get_db
from schemas import CreateUser
from schemas import UpdateUser


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    return user

@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }
@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )

    db.execute(update(User).where(User.id == user_id).values(
        firstname=update_user.firstname,
        lastname=update_user.lastname,
        age=update_user.age
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router.get("/users/{user_id}/tasks")
async def tasks_by_user_id(user_id: int, db: Session = Depends(get_db)):
    tasks = db.execute(select(Task).where(Task.user_id == user_id)).scalars().all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this user")

    return tasks


@router.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_stmt = select(User).where(User.id == user_id)
    user = db.execute(user_stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    tasks_stmt = select(Task).where(Task.user_id == user.id)
    tasks = db.execute(tasks_stmt).scalars().all()

    for task in tasks:
        db.delete(task)

    db.delete(user)
    db.commit()

    return {
        'status_code': 200,
        'transaction': 'User and associated tasks deleted successfully!'
    }
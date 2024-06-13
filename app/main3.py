from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional,List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models,schemas,utils
from .database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


#Create Tables in database
models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/posts")
def get_posts(db:Session = Depends(get_db),response_model=List[schemas.Post]):
    post_data = db.query(models.Post).all()
    #return {"post_data":post_data}
    return post_data

@app.post("/posts", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post:schemas.CreatePost,db:Session = Depends(get_db)):
    # create_user = models.Post(title=post.title,content=post.content,published=post.published)
    create_user = models.Post(**post.dict())
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
    #return {"data": create_user}
    return create_user

@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id: str,db:Session = Depends(get_db),response_model=schemas.Post):
    get_posts = db.query(models.Post).filter(models.Post.id==id).first()
    if not get_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    #return {"post_details": get_posts}
    return get_posts

@app.delete("/posts/{id}")
def delete_post(id: str,db:Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}",response_model=schemas.Post)
def update_post(id: int, post: schemas.CreatePost, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_update = post_query.first()
    
    if post_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )
    
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    db.refresh(post_to_update)
    
    #return {"data": post_query.first()}
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserOut, db: Session = Depends(get_db)):
    try:
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()  # Rollback the transaction in case of error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the user.")


@app.get("/users/{id}", response_model=schemas.UserCreate)
def get_post(id: int, db: Session = Depends(get_db)):
    try:
        post = db.query(models.User).filter(models.User.id == id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
        return post
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the post.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional,List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .. import models,schemas,utils,oauth2
from ..database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


router = APIRouter(
     prefix = "/posts",
     tags=["Posts"]
)

#@router.get("/",response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db:Session = Depends(get_db),currrnt_user:int=Depends(oauth2.get_current_user),limit:int=10,skip:int = 0,search:Optional[str]=""):
    #post_data = db.query(models.Post).filter(models.Post.owner_id == currrnt_user.id).all()
    # post_data = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # print(post_data)
    try:
        posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
        return posts

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
   

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post:schemas.CreatePost,db:Session = Depends(get_db),currrnt_user:int=Depends(oauth2.get_current_user)):
    # create_user = models.Post(title=post.title,content=post.content,published=post.published)
    create_user = models.Post(owner_id=currrnt_user.id,**post.dict())
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
    #return {"data": create_user}
    return create_user

@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id: str,db:Session = Depends(get_db),currrnt_user:int=Depends(oauth2.get_current_user)):
    #get_posts = db.query(models.Post).filter(models.Post.id==id).first()
    # if not get_posts:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    #New Joins Update
    try:
        post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with id: {id} was not found")
        
        return post
     
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id}")
def delete_post(id: str,db:Session = Depends(get_db),currrnt_user:int=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id==id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if post.first().owner_id != currrnt_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform a action")

    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.Post)
def update_post(id: int, post: schemas.CreatePost, db: Session = Depends(get_db),currrnt_user:int=Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_update = post_query.first()

  
    if post_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )
    
    if post_to_update.owner_id != currrnt_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform a action")
    
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    db.refresh(post_to_update)
    
    #return {"data": post_query.first()}
    return post_query.first()
from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

my_posts = [{"title":"title of post 1","content":"content of post 1","id":1},
{"title":"title of post 1","content":"content of post 1","id":2},{"title":"title of post 1","content":"content of post 1","id":3}]

class Post(BaseModel):
    title:str
    content:str
    published: bool = True   #default True
    rating: Optional[int] = None

#PostSql DataBase Connection
while True:
        try:
            conn = psycopg2.connect(host='localhost',database='fastApi',user="postgres",password='Password(1111)!',cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            print("DataBase Connection Is Successfully")
            break
        except Exception as error:
            print("Connection to database is faild")
            print("Error:",error)
            time.sleep(2)

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
           return p
    

@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data":posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""
        INSERT INTO posts (title, content, published) 
        VALUES (%s, %s, %s) RETURNING *
    """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: str):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return {"post_details": post}


@app.delete("/posts/{id}")
def delete_post(id:str):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return {"post_details": post}


@app.put("/posts/{id}")
def update_post(id:str,post:Post):
    cursor.execute(""" UPDATE posts SET title=%s,content=%s,published=%s WHERE id=%s RETURNING * """,(post.title,post.content,post.published,id,))
    conn.commit()
    updated_post = cursor.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return {"post_details": updated_post}

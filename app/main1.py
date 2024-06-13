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
    

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/posts")
async def get_posts():
    return {"data":my_posts}

# @app.post("/createpost")
# async def create_post(payload:dict = Body(...)):
#     return {"new_post":f"title {payload['title']} content:{payload['content']}"}

@app.post("/createpost", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    # print(post.rating)  # Uncomment if you have a rating field in the Post model
    # print(post.dict())  # Print as key-value pair
    # print(post)         # Print the post object
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 9999999)
    my_posts.append(post_dict)
    return {"data": post_dict}


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
           return p

def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return None

@app.get("/getposts/{id}")
async def get_post(id: int, response: Response):
    check_post = find_post(id)
    if not check_post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message':f"post with id : {id} not found"}
        #Second Way
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} was not found")
    return {"post_details": check_post}

"""
Developed By Abhay Singh Kathayat
"""

@app.get("/posts/latests")
def get_latests_post():
    post = my_posts[len(my_posts)-1]
    return {"details":post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"Post with id {id} not found")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
async def update_post(id:int,post:Post):
      index = find_index_post(id)
      if index is None:
         raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"Post with id {id} not found")
      post_dict = post.dict()
      post_dict["id"] = id
      my_posts[index] = post_dict
      return {"data": post_dict}


#5432 PostGrace Port Number 
#DataBase Returning Statement
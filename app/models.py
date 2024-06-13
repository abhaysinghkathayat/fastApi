from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

class Post(Base):
    __tablename__ = "posts"  # Name of the table in the database

    id = Column(Integer, primary_key=True, nullable=False)  # Unique identifier for each post
    title = Column(String, nullable=False)  # Title of the post, cannot be null
    content = Column(String, nullable=False)  # Content of the post, cannot be null
    published = Column(Boolean, nullable=False, server_default=text('TRUE'))  # Publish status, defaults to True
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))  # Timestamp of post creation
    owner_id = Column(Integer,ForeignKey("user.id",ondelete="CASCADE"),nullable=False)

    owner = Relationship("User")

class User(Base):
    __tablename__= "user"
    id = Column(Integer, primary_key=True, nullable=False)
    email= Column(String, nullable=False, unique=True)
    password= Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)



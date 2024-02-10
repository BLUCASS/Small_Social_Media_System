from sqlalchemy import create_engine, String, Integer, Column, ForeignKey
from sqlalchemy.orm import declarative_base

# Creating the engine
engine = create_engine('sqlite:///info.db')

# Creating the base
Base = declarative_base()

# Creating the class for the table
class UserDb(Base):

    '''Shaping the table for the database.'''
    __tablename__ = 'user_db'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)


class UserPosts(Base):

    __tablename__ = 'user_posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_db.id"), nullable=False)
    posts = Column(String, nullable=True)


# Inserting the table into the database
Base.metadata.create_all(engine)
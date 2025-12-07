from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    author: str

class PostRead(PostCreate):
    id: int

    class Config:
        orm_mode = True
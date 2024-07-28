from ninja import Schema
from pydantic import constr
from datetime import datetime
from typing import List


class PostSchema(Schema):
    text: constr(min_length=10, max_length=102400)


class RetrievePostSchema(Schema):
    id: int
    user_id: int
    text: str
    created_date: datetime

    class Config:
        from_attributes = True


class RetrievePostCommentsSchema(Schema):
    id: int
    user_id: int
    text: str
    created_date: datetime
    descendants: List['RetrievePostCommentsSchema'] = []

    class Config:
        from_attributes = True


RetrievePostCommentsSchema.model_rebuild()

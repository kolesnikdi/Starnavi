from ninja import Schema
from pydantic import constr, conint, confloat
from datetime import datetime
from typing import List


class PostSettingsSchema(Schema):
    is_ai_reply: bool
    time_sleep: conint(ge=0, le=7200)
    creativity: confloat(ge=0.0, le=1.0)

    class Config:
        from_attributes = True


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

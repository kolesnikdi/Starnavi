from ninja import Schema
from pydantic import constr, conint, confloat, RootModel, BaseModel
from datetime import datetime
from typing import List, Dict, Optional


class PostCommentBreakdown(BaseModel):
    blocked_comments: int
    clean_comments: int


class DailyBreakdownDate(BaseModel):
    total_blocked_comments: int
    total_clean_comments: int
    posts: Optional[Dict[str, PostCommentBreakdown]] = None


class DailyBreakdownResponseSchema(RootModel):
    root: Dict[str, DailyBreakdownDate]


DailyBreakdownResponseSchema.model_rebuild()


class PostSettingsSchema(Schema):
    is_ai_reply: bool
    time_sleep: conint(ge=0, le=7200)
    creativity: confloat(ge=0.0, le=1.0)
    reply_or_dialogue: int
    base_reply: str

    class Config:
        from_attributes = True


class CreatePostSchema(Schema):
    text: constr(min_length=10, max_length=102400)


class PostSortSchema(Schema):
    path: str
    id: int
    user_id: int
    text: str
    created_date: datetime
    is_blocked: bool

    class Config:
        from_attributes = True


class PostSchema(Schema):
    id: int
    user_id: int
    text: str
    created_date: datetime
    is_blocked: bool

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

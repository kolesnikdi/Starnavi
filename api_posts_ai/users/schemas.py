from ninja import Schema
from pydantic import EmailStr, constr


class UserCreateSchema(Schema):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8)
    email: EmailStr

    class Config:
        orm_mode = True


class UserLoginSchema(Schema):
    username: str
    password: str

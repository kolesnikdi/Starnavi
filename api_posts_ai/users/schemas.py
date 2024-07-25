from ninja import Schema
from pydantic import EmailStr, SecretStr, constr


class UserCreateSchema(Schema):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8)
    email: EmailStr

    class Config:
        from_attributes = True


class UserCreateSuccessSchema(UserCreateSchema):
    id: int


class ErrorSchema(Schema):
    message: str


class UserLoginSchema(Schema):
    username: str
    password: SecretStr

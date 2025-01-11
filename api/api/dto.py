
from pydantic import BaseModel

class CreateUserIn(BaseModel):
    username: str
    fullname: str
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

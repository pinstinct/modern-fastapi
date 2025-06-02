from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str


class SignInUSer(PublicUser):
    password: str


class PrivateUser(PublicUser):
    hash: str

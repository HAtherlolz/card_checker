from pydantic import BaseModel, EmailStr


class ProfileRetrieve(BaseModel):
    """ Retrieve Profile schema """
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class ProfileEmail(BaseModel):
    """ Email Profile schema """
    email: EmailStr


class ProfileCreate(BaseModel):
    """ Create Profile schema """
    email: EmailStr
    password: str


class NewPassword(BaseModel):
    """
        Schema for checking password in reset endpoint
    """
    token: str
    password: str
    new_password: str


# ===============Tokens==============
class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(RefreshToken):
    access_token: str


class TokenData(BaseModel):
    email: str | None
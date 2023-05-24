import re
from pydantic import BaseModel, EmailStr, validator


class ProfileRetrieve(BaseModel):
    """ Retrieve Profile schema """
    id: int
    email: EmailStr
    guid: str | None

    class Config:
        orm_mode = True


class ProfileEmail(BaseModel):
    """ Email Profile schema """
    email: EmailStr


class ProfileCreate(BaseModel):
    """ Create Profile schema """
    email: EmailStr
    password: str

    @validator("password")
    def password_validator(cls, v: str) -> str:
        password_regex = r"^(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(password_regex, v):
            raise ValueError("The password must contains at least 8 charset, at least 1 uppercase charset")
        return v


class ProfileCreateWithGUID(ProfileCreate):
    """ Create profile with guid """
    guid: str


class WidgetURL(BaseModel):
    """ Schema for getting url """
    url: str


class MxUserMemberGuids(BaseModel):
    """ Schema for getting member_guid """
    user_guid: str
    member_guid: str


class NewPassword(BaseModel):
    """
        Schema for checking password in reset endpoint
    """
    token: str
    password: str
    new_password: str

    @validator("password")
    def password_validator(cls, v: str) -> str:
        password_regex = r"^(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(password_regex, v):
            raise ValueError("The password must contains at least 8 charset, at least 1 uppercase charset")
        return v


# ===============Tokens==============
class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(RefreshToken):
    access_token: str


class TokenData(BaseModel):
    email: str | None

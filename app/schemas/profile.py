from pydantic import BaseModel, EmailStr


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


class ProfileCreateWithGUID(ProfileCreate):
    """ Create profile with guid """
    guid: str


class WidgetURL(BaseModel):
    """ Schema for getting url """
    url: str


class Webhook(BaseModel):
    action: str | None
    connection_status: str | None
    connection_status_id: int | None
    connection_status_message: str | None
    member_guid: str | None
    type: str | None
    user_guid: str | None


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

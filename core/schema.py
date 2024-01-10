from typing import List
from pydantic import BaseModel, Field, EmailStr


class UserDetails(BaseModel):
    user_name: str = Field("Enter the user name")
    first_name: str = Field("Enter the First Name", pattern=r'^[A-Z]{1}\D{1,}')
    last_name: str = Field("Enter the Last Name", pattern=r'^[A-Z]{1}\D{1,}')
    email: EmailStr = Field("Enter the email address")
    password: str = Field("Enter valid Password")
    location: str = Field("Enter the Location")
    phone: int = Field("Enter the phone Number")
    # is_verified: bool


class UserLogin(BaseModel):
    user_name: str = Field("Enter user name")
    password: str = Field("Enter Password")


class UpdateNotes(BaseModel):
    title: str = Field("Enter the title of note.")
    description: str = Field("Enter description")
    color: str = Field('Enter color')


class LabelDetails(BaseModel):
    name: str = Field("Enter the label name")


class CollaboratorDetails(BaseModel):
    note_id: int
    user_ids: List[int]
    
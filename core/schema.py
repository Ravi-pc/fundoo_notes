from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserDetails(BaseModel):
    user_name: EmailStr = Field("", title="Enter the user name")
    first_name: str = Field("", title="Enter the First Name", pattern=r'^[A-Z]{1}\D{3,}')
    last_name: str = Field("", title="Enter the Last Name", pattern=r'^[A-Z]{1}\D{3,}')
    password: str = Field("", title="Enter valid Password")


class UserLogin(BaseModel):
    user_name: str = Field("", title="Enter user name")
    password: str = Field("", title="Enter Password")


class UpdateNotes(BaseModel):
    title: str = Field("Enter the title of note.")
    description: str = Field("Enter description")
    color: str = Field("Enter color")


class LabelDetails(BaseModel):
    name: str = Field("Enter the label name")


class CollaboratorDetails(BaseModel):
    note_id: int
    user_ids: List[int]
    
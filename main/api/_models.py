from pydantic import BaseModel
from typing import List

class CBmodel(BaseModel):
    pointmap:List
    connected_points:List[int]

class NameID(BaseModel):
    username:str
    userID:int

class CBpkg(BaseModel):
    user:NameID
    cbmodel:CBmodel
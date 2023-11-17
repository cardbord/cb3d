from pydantic import BaseModel
from typing import List

class CBmodel(BaseModel):
    pointmap:List
    connected_points:List[int]
    
class registrationItem(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str
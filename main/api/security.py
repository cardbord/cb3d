from _models import NameID
from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from typing import Annotated
from sqlalchemy import Table
from databases import Database

SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")
class UploadHandler:
    def __init__(self,db:Database,users_schema:Table):
        self.pwd_ctx = CryptContext(schemes=["bcrypt"],deprecated="auto")
        self.db = db
        self.users_schema = users_schema
        
    
    async def _get_user(self,identifier):
        query = self.users_schema.select().where(self.users_schema.c.userID==identifier)
        return await self.db.execute(query)

    def authenticate_password(self,userID,password):
        user = self._get_user(userID)
        if user:
            user = eval(user)

            if self.pwd_ctx.verify(password,user['password']):
                return user
        return None
    
    def create_access_token(self,data:dict):
        data.update({"exp":datetime.utcnow()+timedelta(hours=10)}) #should be long enough to use, but not too long to leave open for bad actors
        return jwt.encode(data,SECRET)
    
    async def authenticate_token(self,token:Annotated[str,oauth2scheme]):
        try:
            decoded_token_payload = jwt.decode(token,SECRET)
            userID = decoded_token_payload.get("userID")
            if userID:
                user = self._get_user(userID)
                if user:
                    return user
                else:
                    raise HTTPException(status_code=401,detail="Bad credentials",headers={"WWW-Authenticate":"Bearer"})
        except JWTError as e:
            raise HTTPException(status_code=401,detail=str(e),headers={"WWW-Authenticate":"Bearer"})

    async def hash_password(password):
        return bcrypt.hash(password)
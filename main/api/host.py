from fastapi import FastAPI, Depends
import sqlalchemy
from databases import Database
from _models import *
from random import sample
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from security import UploadHandler
from passlib.hash import bcrypt

room_id = sample("QqWwEeRrTtYyUuIiOoPpAaSsDdFfGgHhJjKkLlZzXxCcVvBbNnMm1234567890",6)
print(room_id)

host_service = FastAPI()

DATABASE_URL = "postgresql://postgres:qwerty@localhost:5432"
metadata = sqlalchemy.MetaData()

models = sqlalchemy.Table(
    "models",
    metadata,
    sqlalchemy.Column("pointmap",sqlalchemy.String),
    sqlalchemy.Column("connected_points",sqlalchemy.String)
)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("userID",sqlalchemy.String),
    sqlalchemy.Column("password",sqlalchemy.String)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

database = Database(DATABASE_URL)

authentication_session = UploadHandler(database,users)

@host_service.on_event("startup")
async def startup():
    await database.connect()

@host_service.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@host_service.get("/models/",dependencies=[Depends(authentication_session.authenticate_token)])
async def fetch_models():
    query = models.select()
    return await database.fetch_all(query)
    

@host_service.patch("/upload/",dependencies=[Depends(authentication_session.authenticate_token)])
async def upload_model(json:CBmodel):
    query = models.insert().values(pointmap=str(json.pointmap),connected_points=str(json.connected_points))
    result = await database.execute(query)
    return {**json.model_dump(), "id":result}

@host_service.post("/register/")
async def register(json:registrationItem):
    username_exists = models.select().where(users.c.userID==json.username)

    if username_exists != None:
        query = users.insert().values(userID=json.username,password=bcrypt.hash(json.password))
        result= await database.execute(query)
        return {**json.model_dump(), "id":result}
    else:
        raise HTTPException(status_code=401,detail="Username is already registered.")
    
@host_service.post("/login/",response_model = Token)
async def login(data:Annotated[OAuth2PasswordRequestForm,Depends()]):
    user =  authentication_session.authenticate_password(data.username,data.password)
    if user:
        access_token = authentication_session.create_access_token(data={"userID":data.username})
        return Token(access_token=access_token,token_type="bearer")
    
    raise HTTPException(status_code=401,detail="Invalid credentials",headers={"WWW-Authenticate":"Bearer"})
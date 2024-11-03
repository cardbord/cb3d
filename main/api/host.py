from fastapi import FastAPI, Depends
import sqlalchemy
from databases import Database
from random import sample
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from passlib.hash import bcrypt
from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
import datetime
from pydantic import BaseModel
import sys

class CBmodel(BaseModel): #to be used in model submission to the database
    modelname:str
    modelData:str #use the same stream used in .CBmodels
    username:str
    
class registrationItem(BaseModel): #to be used in registration - to add user accounts to the database
    username:str
    password:str
    roomid:str

class Token(BaseModel): #to be used when returning tokens back after logging in
    access_token:str
    token_type:str


SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" #secret key - generated with openssl
oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")
class UploadHandler: #security system to authenticate users by their credentials
    def __init__(self,db:Database,users_schema:sqlalchemy.Table):
        self.pwd_ctx = CryptContext(schemes=["bcrypt"],deprecated="auto")
        self.db = db
        self.users_schema = users_schema
        
    
    async def _get_user(self,identifier):
        query = self.users_schema.select().where(self.users_schema.c.userID==identifier)
        return await self.db.fetch_one(query)

    async def authenticate_password(self,userID,password):
        user = await self._get_user(userID)
        if user and self.pwd_ctx.verify(password,user.password):
            return {'userID':user.userID, 'password':user.password}    
        return None
    
    def create_access_token(self,data:dict):
        data.update({"exp":datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=10)}) #should be long enough to use, but not too long to leave open for bad actors
        return jwt.encode(data,SECRET)
    
    async def authenticate_token(self,token:Annotated[str,Depends(oauth2scheme)]): #token verificaiton after user is logged in
        try:
            decoded_token_payload = jwt.decode(token,SECRET) #verification process in reverse, returning  original user
            userID = decoded_token_payload.get("userID")

            if userID:
                user = await self._get_user(userID) 
                if user:
                    return user
                else:
                    raise HTTPException(status_code=401,detail="Bad credentials",headers={"WWW-Authenticate":"Bearer"})
        except JWTError as e:
            raise HTTPException(status_code=401,detail=str(e),headers={"WWW-Authenticate":"Bearer"})


global room_id
room_id = sample("QqWwEeRrTtYyUuIiOoPpAaSsDdFfGgHhJjKkLlZzXxCcVvBbNnMm1234567890",6) #sample random letters and numbers


host_service = FastAPI()

DATABASE_URL = "postgresql://postgres:qwerty@localhost:5432" #test database

metadata = sqlalchemy.MetaData()

models = sqlalchemy.Table( #models table
    "models",
    metadata,
    sqlalchemy.Column("modelname",sqlalchemy.String),
    sqlalchemy.Column("modeldata",sqlalchemy.String),
    sqlalchemy.Column("username",sqlalchemy.String)
) #no primary key as all of these will be loaded at once. they cannot be searched for

users = sqlalchemy.Table( #users table
    "users",
    metadata,
    sqlalchemy.Column("userID",sqlalchemy.String, primary_key=True), #a primary key is needed here as userID is searched for during verification
    sqlalchemy.Column("password",sqlalchemy.String)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

database = Database(DATABASE_URL)

authentication_session = UploadHandler(database,users)

@host_service.on_event("startup")
async def startup():
    global room_id
    if len(sys.argv)>1:
        room_id = sys.argv[1][4:]
    title = '\033[96m'
    print(f'''{title}---------------------------------------
    welcome to CB3D model sharing API!
          
    Using database {DATABASE_URL}
    Your room ID is {room_id}
    Connecting now...
---------------------------------------          
---------------------------------------
          ''')
    await database.connect()

@host_service.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@host_service.get("/models/",dependencies=[Depends(authentication_session.authenticate_token)]) #authenticates the token via the UploadHandler
async def fetch_models():
    query = models.select()
    return await database.fetch_all(query) #select all and return
    

@host_service.post("/upload/",dependencies=[Depends(authentication_session.authenticate_token)]) #authenticates the token via the UploadHandler
async def upload_model(json:CBmodel):
    query = models.insert().values(modelname=str(json.modelname), modeldata=str(json.modelData), username=str(json.username)) #equivalent of INSERT INTO models, VALUES (values)
    result = await database.execute(query)
    return {**json.model_dump(), "id":result}

@host_service.post("/register/") #register a user account
async def register(json:registrationItem):
    if json.roomid == room_id: #if roomID is correct
        username_exists = models.select().where(users.c.userID==json.username)

        if username_exists != None:
            query = users.insert().values(userID=json.username,password=bcrypt.hash(json.password)) #insert a username and hashed password
            result= await database.execute(query)
            return {**json.model_dump(), "id":result} #return the same data that was submitted, with a status code
        else:
            raise HTTPException(status_code=401,detail="Username is already registered.")
    else:
        raise HTTPException(status_code=401, detail="Invalid room ID")
        
@host_service.post("/login/",response_model = Token) #authentication for a pre-existing user account
async def login(data:Annotated[OAuth2PasswordRequestForm,Depends()]): #requires an encoded password form
    user =  await authentication_session.authenticate_password(data.username,data.password) #verifies user and password
    if user:
        access_token = authentication_session.create_access_token(data={"userID":data.username}) #creates and returns token
        return Token(access_token=access_token,token_type="bearer")
    
    raise HTTPException(status_code=401,detail="Invalid credentials",headers={"WWW-Authenticate":"Bearer"})


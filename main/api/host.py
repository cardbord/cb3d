from fastapi import FastAPI
import sqlalchemy
from databases import Database
from _models import *
from typing import List
from random import sample


room_id = sample("QqWwEeRrTtYyUuIiOoPpAaSsDdFfGgHhJjKkLlZzXxCcVvBbNnMm1234567890",6)
print(room_id)

host_service = FastAPI()

DATABASE_URL = ''
metadata = sqlalchemy.MetaData()

models = sqlalchemy.Table(
    "models",
    metadata,
    sqlalchemy.Column("pointmap",sqlalchemy.String),
    sqlalchemy.Column("connected_points",sqlalchemy.String)
)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread":False})
metadata.create_all(engine)

database = Database(DATABASE_URL)

@host_service.on_event("startup")
async def startup():
    await database.connect()

@host_service.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@host_service.get("/models/",response_model=List[CBmodel])
async def fetch_models():
    query = models.select()
    return await database.fetch_all(query)

@host_service.patch("/upload/")
async def upload_model(json:CBmodel):
    query = models.insert().values(pointmap=json.pointmap,connected_points=json.connected_points)
    result = await database.execute(query)
    return {**json.model_dump(), "id":result}


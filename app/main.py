# main.py
import asyncio
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List
import os
import numba

import strawberry
from strawberry.fastapi import GraphQLRouter

from BookGraphqlSchema import Query

import Config

from database import db

app = FastAPI()

# Get MongoDB connection details from environment variables
MONGO_HOST = Config.MONGO_HOST
MONGO_PORT = Config.MONGO_PORT
MONGO_DB_NAME = Config.MONGO_DB_NAME
MONGO_COLLECTION_NAME = Config.MONGO_COLLECTION_NAME
MONGO_USER = Config.MONGO_USER
MONGO_PASSWORD = Config.MONGO_PASSWORD

schema = strawberry.Schema(Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

async def get_db_client() -> AsyncIOMotorClient:
    return db.client

class Book(BaseModel):
    title: str
    author: str

async def populate_db_if_empty():
    if await app.mongodb[MONGO_COLLECTION_NAME].count_documents({}) == 0:
        await app.mongodb[MONGO_COLLECTION_NAME].insert_many(
            [
                {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
                { "title": "The Beutiful and Damned", "author": "F. Scott Fitzgerald"},
                {"title": "The Catcher in the Rye", "author": "J. D. Salinger"},
                {"title": "The Grapes of Wrath", "author": "John Steinbeck"},
            ]
        )

@app.on_event("startup")
async def startup():
    await asyncio.sleep(5)
    # app.mongodb_client = AsyncIOMotorClient(
    #     f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    # )
    app.mongodb_client = await get_db_client()
    app.mongodb = app.mongodb_client[MONGO_DB_NAME]
    await populate_db_if_empty()

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_client.close()

@numba.jit(cache=True, nopython=True)
@app.get("/books", response_model=List[Book])
async def get_books():
    books = []
    async for book in app.mongodb[MONGO_COLLECTION_NAME].find():
        books.append(book)
    return books


@app.get("/book/{book_name}", response_model=Book)
async def get_book(book_name: str):
    book = await app.mongodb[MONGO_COLLECTION_NAME].find_one({"title": book_name})
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")
    
@app.post("/book", response_model=Book)
async def create_book(book: Book):
    await app.mongodb[MONGO_COLLECTION_NAME].insert_one(book.dict())
    return book
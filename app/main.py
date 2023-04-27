# main.py
import asyncio
from services.prime_service import invokePrimeWorkflow
from services.factorial_service import invokeFactorialWorkflow
from services.prime_factorial_service import invokePrimeFactorialWorkflow
from fastapi import FastAPI, HTTPException, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List
import os
import numba

from config import logger as log

import strawberry
from strawberry.fastapi import GraphQLRouter

from BookGraphqlService import BooksQuery

import config

import database
from memgraphDatabase import memgraphdb

from fastapi.responses import HTMLResponse
from jinja2 import Environment, Template, FileSystemLoader
import yaml

from activities import find_factorial_activity, find_prime
from workflows.prime_workflow import FindPrimeFlow
from workflows.prime_factorial_workflow import PrimeFactorialFlow
from workflows.factorial_workflow import FactorialFlow
from temporal_worker import start_temporal_worker

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# Get MongoDB connection details from environment variables
MONGO_DB_NAME = config.MONGO_DB_NAME
MONGO_COLLECTION_NAME = config.MONGO_COLLECTION_NAME

schema = strawberry.Schema(BooksQuery)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

class Book(BaseModel):
    title: str
    author: str

async def populate_db_if_empty():
    log.info("DB is empty. Populating with sample data.")
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
    log.info("Waiting for MongoDB and Temporal Worker to start up...")
    await asyncio.sleep(20)
    app.mongodb_client = await database.get_db_client()
    app.mongodb = app.mongodb_client[MONGO_DB_NAME]
    await populate_db_if_empty()
    await start_temporal_worker(config.temporal_url,
                                config.temporal_namespace,
                                config.temporal_queue_name, 
                                [FindPrimeFlow,
                                 FactorialFlow,
                                 PrimeFactorialFlow], 
                                [find_prime,
                                 find_factorial_activity])
    app.memgraph_client = memgraphdb

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_client.close()

@numba.jit(cache=True, nopython=True)
@app.get("/books", summary="Get all books", response_model=List[Book])
async def get_books():
    books = []
    async for book in app.mongodb[MONGO_COLLECTION_NAME].find():
        books.append(book)
    return books


@app.get("/book/{book_name}", summary="Get book by title", response_model=Book)
async def get_book(book_name: str):
    book = await app.mongodb[MONGO_COLLECTION_NAME].find_one({"title": book_name})
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")

@app.get("/invokePrimeFlow/{number}",
         summary="invoke Prime Flow", 
         description="Find the Nth prime number Ex: 5 returns 11, 10 returns 29, 100 returns 541")
async def invokePrimeFlow(number: int):
    log.info(f"invokePrimeFlow {number}")
    try:
        prime = await invokePrimeWorkflow(number)
        log.debug(f"Prime: {prime}")
        return HTMLResponse(content=f"Prime: {prime}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)

@app.get("/invokeFactorialFlow/{number}",
         summary="invoke Factorial Flow", 
         description="Find f(n) = (n)! Ex: 5 returns 120, 10 returns 3628800, 100 returns 9.33262154439441e+157")
async def invokeFactorialFlow(number: int):
    log.info(f"invokeFactorialFlow {number}")
    try:
        n = await invokeFactorialWorkflow(number)
        log.debug(f"Factorial: {n}")
        return HTMLResponse(content=f"Factorial: {n}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)
    
@app.get("/invokePrimeFactorialFlow/{number}",
         summary="invoke Prime Factorial Flow", 
         description="Find the nth prime number and then find the factorial of that number, Ex: 10th prime = 29, 29! = 8.84176199E30")
async def invokePrimeFactorialFlow(number: int):
    log.info(f"invokePrimeFactorialFlow {number}")
    try:
        n = await invokePrimeFactorialWorkflow(number)
        log.debug(f"invokePrimeFactorialWorkflow: {n}")
        return HTMLResponse(content=f"invokePrimeFactorialFlow: {n}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)
    
    
@app.post("/book", summary="Add new book to db", response_model=Book)
async def create_book(book: Book):
    await app.mongodb[MONGO_COLLECTION_NAME].insert_one(book.dict())
    return book

@app.post("/render_template/",
         summary="render a jinja template", 
         description="Provide a Jinja template and a YAML file with parameters")
async def render_template(template: UploadFile = File(...), params: UploadFile = File(...)) -> HTMLResponse:
    try:
        # Read Jinja template
        template_str = (await template.read()).decode("utf-8")
        jinja_template = Template(template_str, trim_blocks=True, lstrip_blocks=True)
        log.debug(f"template_str {jinja_template}")

        # Read YAML parameters
        params_str = (await params.read()).decode("utf-8")
        template_params = yaml.safe_load(params_str)
        log.debug(f"params_str {template_params}")

        # Render template with parameters
        rendered_template = jinja_template.render(**template_params)
        log.debug(f"rendered_template {rendered_template}")

        return HTMLResponse(content=rendered_template, status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)

@app.get("/memgraph/books", summary="Get all books from Memgraph", response_model=List[Book])
async def get_books_from_memgraph():
    booksQuery = """MATCH (n:Book)
           RETURN n as result"""
    results = app.memgraph_client.execute_and_fetch(booksQuery)
    results = app.memgraph_client.serialize_results_to_json(results)
    log.debug(f"results {results}")
    return JSONResponse(content=jsonable_encoder(results))
    
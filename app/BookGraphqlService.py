from typing import List
import strawberry
import database
import config as config
from config import logger as log

@strawberry.type
class Book:
    title: str
    author: str

async def get_books_db(title: str = None, author: str = None) -> List[Book]:
    log.debug(f"get_books_db {title} {author}")
    query = {}

    if title:
        query["title"] = title

    if author:
        query["author"] = author

    mongodb_client = await database.get_db_client()
    mongodb = mongodb_client[config.MONGO_DB_NAME]
    books_cursor =  mongodb[config.MONGO_COLLECTION_NAME].find(query)

    books  = []
    async for book in books_cursor:
        log.debug(f"book {book}")
        books.append(
            Book(
                title=book["title"],
                author=book["author"],
            )
        )

    log.debug(f"exit get_books_db {books}")
    return books

@strawberry.type
class BooksQuery:
    books: List[Book] = strawberry.field(resolver=get_books_db)
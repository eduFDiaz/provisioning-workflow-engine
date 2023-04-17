import typing
import strawberry
# import app

@strawberry.type
class Book:
    title: str
    author: str


@strawberry.type
class Query:
    books: typing.List[Book]

def get_books(title: str = None, author: str = None):
    books = [
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
        ),
        Book(
            title="The Beutiful and Damned",
            author="F. Scott Fitzgerald",
        ),
        Book(
            title="The Catcher in the Rye",
            author="J. D. Salinger",
        ),
        Book(
            title="The Grapes of Wrath",
            author="John Steinbeck",
        ),
    ]

    if title:
        books = [book for book in books if book.title == title]
    
    if author:
        books = [book for book in books if book.author == author]

    return books

# def get_books_db(title: str = None, author: str = None):
#     query = {}

#     if title:
#         query["title"] = title

#     if author:
#         query["author"] = author

        
#     mongodb_client = await app.get_db_client()
#     books_cursor =  await app.get_db_client()
#     mongodb[Config.MONGO_COLLECTION_NAME].find(query)

#     books = [
#         Book(
#             title=book["title"],
#             author=book["author"],
#         ) for book in books_cursor
#     ]

#     return books


@strawberry.type
class Query:
    books: typing.List[Book] = strawberry.field(resolver=get_books)
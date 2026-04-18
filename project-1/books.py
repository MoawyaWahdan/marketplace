from fastapi import FastAPI, Path, Query, Cookie, Header, HTTPException, status, Response, File, UploadFile
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import date
from fastapi.encoders import jsonable_encoder


app = FastAPI()

books = [
    {"id": 1, "title": "FastAPI Guide", "author": "Alice",
         "year": 2023, "price": 20, "published_date": date(2025, 3, 1),
        "tags":["FastAPI"]},

    {"id": 2, "title": "Python Basics", "author": "Bob", 
        "year": 2021, "price": 25, "published_date": date(2020, 7, 2),
        "tags":["python", "beginner"]},
    {"id": 3, "title": "Advanced Python", "author": "Alice", 
        "year": 2022, "price": 50, "published_date": date(2023, 4, 9),
        "tags":["Advanced"]},
    {"id": 4, "title": "Noaha dreamy", "author": "Alice", 
        "year": 2020, "price": 50, "published_date": date(2020, 4, 9),
        "tags":["Advanced"]},
]


Tag = Annotated[str, Field(min_length=2, max_length=20)]

class Book(BaseModel):
    id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=70)
    author: str = Field(min_length=1, max_length=30)
    year: int = Field(ge=1900)
    price: int = Field(ge=0)
    published_date: date = Field(ge=date(1900, 1, 1), le=date.today())
    tags: list[Tag] = Field(default_factory=list, min_length=1, max_length=5)


@app.get("/books/{book_id}", response_model=Book, tags=["Books"], summary="Get book by id") 
async def get_book_by_id(book_id: Annotated[int, Path(title="Book ID", 
                                                    description="The unique identifier of the book.",
                                                    gt=0,
                                                    lt=100)]):
    """
        Return the book with given book_id.<br>
        **book_id**: Psitive value > 0
    """
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
 


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}
    author: str | None = Field(None, min_length=3, max_length = 50)
    title: str | None = Field(None, min_length=3, max_length = 40)
    limit: int = Field(5, gt=0, le=15)
    min_price: int = Field(0, ge=0)
    published_after: date = Field(default=date(1960,1,1), description="Return books published after this date")
    tags: list[Tag] = Field(default_factory=list)


@app.get("/books", 
         response_model=list[Book], 
         tags=["Books"],
         summary="Search for books",
         description="Search for books that match filters...",
         response_description="List of books matching filters",
         responses={
            400: {"description": "Invalid filters"},
            404: {"description": "No books found"}
         })
async def search_books(filters: Annotated[FilterParams, Query()],
                    response: Response,
                    last_author: Annotated[str | None, Cookie()] = None,
                    x_author: Annotated[str | None, Header()] = None,
                       ):
 


    if filters.author:
        response.set_cookie(key="last_author", value=filters.author, max_age=600)

    target_author = filters.author or x_author or last_author
    print("target_author", target_author)
    books_res = []
    for book in books:
        if len(books_res) == filters.limit:
            break
        if target_author and  book["author"].lower() != target_author.lower():
            continue
        if filters.title and filters.title.lower() not in  book["title"].lower():
            continue

        if book["price"] < filters.min_price :
            continue
        if book["published_date"] < filters.published_after :
            continue
                
        if filters.tags and not any(tag in book["tags"] for tag in filters.tags):
                    continue
        
        books_res.append(book)


    return books_res


def book_id_exist(book_id: int ):
    for book in books:
        if book["id"] == book_id:
            return True
    return False

def book_exist(book):
    for b in books:
        if b["author"]== book["author"] and \
            b["year"] == book["year"] and \
            b["title"] == book["title"]:
            return True
    return False

@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=Book)            
async def create_book(book: Book):
    new_id = len(books) + 1
 
    book_dict = book.model_dump()
    if(book_exist(book_dict)):
        raise HTTPException(status_code=400, detail="This book was already added")
 
    if book.id is not None:
        if(book_id_exist(book.id)):
            raise HTTPException(status_code=400, detail="This book_id was already added")
        new_id = book.id
    
    book_dict["id"] = new_id

    books.append(book_dict)
    return book_dict


def get_book(id: int):
    for book in books:
        if book["id"] == id:
            return book
    return None

class BookParams(BaseModel):
    title: str = Field(min_length=1, max_length=70)
    author: str = Field(min_length=1, max_length=30)
    year: int  = Field(ge=1900)
    price: int  = Field(ge=0)
    published_date: date 
    tags: list[Tag]

def duplicate_book(book_id:int, title: str, author: str):
    for book in books:
        if book["id"] == book_id:
            continue
        if title.lower() == book["title"].lower() and \
            book["author"].lower() == author.lower():
                return True
    
    return False

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_params: BookParams, book_id: Annotated[int, Path(title="Book ID", 
                                                    description="The unique identifier of the book.",
                                                    gt=0,
                                                    lt=100)]):
    book = get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} doesn't exist")
    
    if duplicate_book(book_id, book_params.title, book_params.author):
        raise HTTPException(status_code=400, detail="Duplicate book")
    
    
    book["title"] = book_params.title
    book["author"] = book_params.author
    book["year"] = book_params.year
    book["price"] = book_params.price
    book["published_date"] = book_params.published_date
    book["tags"] = book_params.tags

    return book


class BookParamsOptional(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=70)
    author: str | None = Field(default=None, min_length=1, max_length=30)
    year: int | None = Field(default=None, ge=1900)
    price: int | None = Field(default=None, ge=0)
    published_date: date | None = None
    tags: list[Tag] | None = None


def duplicate_book_partial(book_id:int, title: str | None, author: str | None):
    target_book = get_book(book_id)
    target_title = target_book["title"] if title is None else title
    target_author = target_book["author"] if author is None else author
    for book in books:
        if book["id"] == book_id:
            continue

        title_match = target_title.lower() == book["title"].lower()
        author_match = target_author.lower() == book["author"].lower()

        if title_match and author_match:
            return True
    
    return False

 

@app.patch("/books/{book_id}", response_model=Book)
async def update_book(book_params: BookParamsOptional, book_id: Annotated[int, Path(title="Book ID", 
                                                    description="The unique identifier of the book.",
                                                    gt=0,
                                                    lt=100)]):
    book = get_book(book_id)
    print("this is patch function")
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} doesn't exist")
    
    if duplicate_book_partial(book_id, book_params.title, book_params.author):
        raise HTTPException(status_code=400, detail="Duplicate book")
    
 
    stored_data_model = Book(**book)
    updated_data = book_params.model_dump(exclude_unset=True)
    updated_data_model = stored_data_model.model_copy(update=updated_data)

 
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books[i] = updated_data_model.model_dump()
            break

    return updated_data_model

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int):
    book = get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_id} doesn't exist")
    books.remove(book)
    
@app.post("/uploadfiles/")
async def create_upload_files(files: Annotated[list[UploadFile], File()]):
    return {"filenames": [file.filename for file in files]}

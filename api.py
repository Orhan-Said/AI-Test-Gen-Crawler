from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from main import process_website

app = FastAPI()


class CrawlRequest(BaseModel):
    url: str


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/crawl")
async def options():
    """
    Handle pre-flight requests for CORS.
    """
    return {"message": "OPTIONS request accepted"}


@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    """
    Start crawling and test generation for the given URL.

    Args:
        request (CrawlRequest): Request body with URL.

    Returns:
        dict: Response with task status.
    """
    asyncio.create_task(process_website(request.url))
    return {"message": "Crawling and test generation started", "url": request.url}

# Run with: uvicorn api:app --reload

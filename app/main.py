import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()  # noqa

from .routers import chat, transcribe  # noqa

openai.api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()

app.include_router(chat.router)
app.include_router(transcribe.router)


@app.get("/")
async def root():
    return "crypto-api"

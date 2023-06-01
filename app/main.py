import asyncio
import logging
import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI

from .dependencies.rnn import app as app_rocketry

logging.basicConfig(level=logging.INFO)

from .routers import chat, transcribe  # noqa

load_dotenv()  # noqa

openai.api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()
session = app_rocketry.session


app.include_router(chat.router)
app.include_router(transcribe.router)


@app.get("/")
async def root():
    return "crypto-api"


@app.on_event("startup")
async def startup():
    "Run Rocketry and FastAPI"
    logging.info("Startup run")
    asyncio.create_task(app_rocketry.serve())
    logging.info("Startup complete")

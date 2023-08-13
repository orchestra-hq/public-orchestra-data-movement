import httpx
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import publicapi
from services.utility.logger import Logger
from services.utility.http import HTTP
from dependencies import get_client_raw


app = FastAPI()
origins = ["http://localhost", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = Logger()
app.include_router(publicapi.router)


@app.on_event("startup")
async def on_startup():
    pass


@app.get("/hello")
async def root():
    return {"message": "Let's move some data!"}

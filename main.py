import httpx
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers.api import api
from webclients.utility.http import HTTP


app = FastAPI()
origins = ["http://localhost", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.on_event("startup")
async def on_startup():
    pass


@app.get("/hello")
async def root():
    return {"message": "Let's move some data!"}

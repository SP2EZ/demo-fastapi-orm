# This script uses Pydantic Model for Structuring HTTP Request and Response

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import posts_orm, users_orm, auth, votes_orm
from . import models
from .database_orm import engine
import socket

# creates the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = ["*"]
# origins = ["https://www.google.com"] ==> this means we are allowing requests from google.com

# by default API calls from other domains will be blocked because of CORS policy
# middleware is like a function that runs before each API request is processed, it controls who can sent the requests and what kind(GET/PUT/DELETE) of requests
# test middleware by running the below from Chrome Browser-> Inspect -> Console after loading google.com
# fetch('http://localhost:8000/').then(res=>res.json()).then(console.log)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_orm.router) # /posts
app.include_router(users_orm.router) # /users
app.include_router(auth.router) # /login
app.include_router(votes_orm.router) # /votes


hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

#print(local_ip)

@app.get("/")
def root():
    return {"message": f"Hello, you have reached API Default Path for Instance: {local_ip}"}


 
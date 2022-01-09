from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import post, user, auth, vote


# creating database models for ORM
# Base.metadata.create_all(bind=engine) # build tables with sqlalchemy natively. commented out because we are using alembic

app = FastAPI()

# we are allowing all origins for testing purposes. when deployed this should be very tightly controlled
origins = ['*']
# cors middleware is responsible for managing resources from different origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# router objects allow us to break the code for different routes to other files
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get('/', tags=['Root'])
def root():
    return {'message': 'I am Root'}

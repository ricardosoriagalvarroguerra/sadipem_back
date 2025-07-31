from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router

# Only allow requests from the production frontend hosted on Railway
origins = ["https://sadipemfront-production.up.railway.app"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Credentials such as cookies or Authorization headers are permitted
    # because the allowed origins list does not contain a wildcard.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "API Brasil SADIPEM"}

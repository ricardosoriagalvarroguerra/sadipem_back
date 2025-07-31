from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router
import os

# Read allowed origins from the environment. If none are provided we
# default to "*".  Credentials are only allowed when a specific origin
# list is supplied to avoid FastAPI raising errors when using "*" with
# credentials enabled.
origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
if origins == ["*"]:
    allow_credentials = False
else:
    allow_credentials = True

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "API Brasil SADIPEM"}

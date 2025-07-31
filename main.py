from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router
import os

# Allowed origin for requests coming from the frontend.  If the
# ALLOWED_ORIGINS environment variable is defined it will override this
# value, allowing multiple comma separated origins.  The default keeps
# the API restricted to the production frontend domain.
default_origin = "https://sadipemfront-production.up.railway.app"
origins_env = os.getenv("ALLOWED_ORIGINS", default_origin)
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

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

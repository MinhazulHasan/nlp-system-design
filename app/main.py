from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import config  # Updated import

app = FastAPI()

from app.api.extraction import extraction_router


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extraction_router, prefix="/api/extraction", tags=["extraction"])
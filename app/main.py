from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# Static files for profile images
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix=settings.API_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

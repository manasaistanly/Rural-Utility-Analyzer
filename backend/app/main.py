from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, bills, analysis, tts

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
# CORS
# Using regex to allow any Vercel deployment (production & previews) + localhost
origin_regex = r"https://.*rural-utility-analyzer.*\.vercel\.app/?|http://localhost:\d+"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os
os.makedirs("data/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="data/uploads"), name="static")

# MongoDB connection lifecycle
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(bills.router, prefix=f"{settings.API_V1_STR}/bills", tags=["bills"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])
app.include_router(tts.router, prefix=f"{settings.API_V1_STR}/tts", tags=["tts"])

@app.get("/")
def root():
    return {"message": "Welcome to Smart Rural Utility Analyzer API - MongoDB Edition"}

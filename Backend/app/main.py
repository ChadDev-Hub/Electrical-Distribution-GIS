from fastapi import FastAPI
from .routes.update_supabase import router
from .routes.map_router import map_router
from .routes.dashboard_router import dashboard_router
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
app = FastAPI()
load_dotenv()
ORIGIN = os.getenv("ORIGIN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN, "https://drive.google.com/thumbnail"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(map_router)
app.include_router(dashboard_router)
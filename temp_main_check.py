from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import asyncio
import threading
import uuid
# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["bigfive"]
ocean_collection = db["ocean_scores"]
tasks_collection = db["tasks"]

print("=" * 60)
print("🚀 FastAPI Backend Started!")
print(f"📊 MongoDB Connected: {MONGO_URL}")
print(f"📦 Database: {db.name}")
print(f"📁 Collection: {ocean_collection.name}")
print("=" * 60)

# FastAPI App
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class OceanScores(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

class OceanData(BaseModel):
    report_id: str
    saved_at: str
    p_factor: float
    ocean_scores: OceanScores
    ocean_normalized: OceanScores


class TaskItem(BaseModel):
    task_name: str
    task_description: Optional[str] = ""  # NEW: Detailed task description
    uploaded_files: Optional[list] = []   # NEW: List of uploaded file paths
    importance_kk: float
    required_time_trk: float
    available_time_tak: float
    report_id: str
    created_at: Optional[str] = None
    status: Optional[str] = "pending"  # pending/running/completed/failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_log: Optional[list] = []

from pfactor import calculate_p_factor
from memory.retention import calculate_retention, calculate_retention_from_timestamp

from memory.confidece import calculate_confidence
from memory.reconstruction import reconstruct_memory
from memory.priority import calculate_priority
from memory.linguistic import generate_npc_response
from adk_agent import execute_task_with_adk

@app.post("/api/save-ocean-scores")
async def save_ocean_scores(data: OceanData):
    """
    Save OCEAN scores and P-Factor to MongoDB
    """
    try:
        ocean_dict = data.model_dump()
        result = ocean_collection.insert_one(ocean_dict)
        print(f"✅ OCEAN Scores Saved | Report ID: {data.report_id} | MongoDB ID: {result.inserted_id}")
        return {"success": True, "message": "OCEAN scores saved successfully"}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timezone
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import asyncio
import threading
import uuid
# Load environment variables
load_dotenv()

app = FastAPI(title="Big Five OCEAN API")

# Enable CORS for your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://made-test-ocean.vercel.app", "https://made-test-ocean-90yqudlau-thaveesha20222110-8749s-projects.vercel.app", "https://made-agent-pfh2k1xj4-thaveesha20222110-8749s-projects.vercel.app", os.getenv("FRONTEND_URL", "https://made-agent-ui.vercel.app")],  # Local + Production URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["bigfive"]  # Database name
ocean_collection = db["ocean_scores"]  # Collection for OCEAN scores
tasks_collection = db["tasks"]         # Collection for Assigned Tasks

print("=" * 60)
print(" FastAPI Backend Started!")
print(f" MongoDB Connected: {MONGO_URL}")
print(f" Database: bigfive")
print(f" Collection: ocean_scores")
print("=" * 60)

# Data models
class OceanScores(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

class OceanData(BaseModel):
    report_id: str
    timestamp: str
    ocean_scores: OceanScores
    ocean_normalized: OceanScores


class TaskItem(BaseModel):
    task_name: str
    task_description: Optional[str] = "" 
    uploaded_files: Optional[list] = []  
    priority_level: Optional[str] = "MED" 
    importance_kk: float
    required_time_trk: float
    available_time_tak: float
    report_id: str
    created_at: Optional[str] = None
    status: Optional[str] = "pending"  
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_log: Optional[list] = []

from pfactor import calculate_p_factor
from memory.retention import calculate_retention, calculate_retention_from_timestamp

from memory.confidece import calculate_confidence
from memory.reconstruction import reconstruct_memory
from memory.priority import calculate_urgency, calculate_priority
from memory.linguistic import generate_npc_response
from adk_agent import execute_task_with_adk

@app.post("/api/save-ocean-scores")
async def save_ocean_scores(data: OceanData):
    
    try:
        print("\n" + "=" * 60)
        print(" RECEIVED DATA FROM FRONTEND")
        print("=" * 60)
        print(f" Report ID: {data.report_id}")
        print(f" Timestamp: {data.timestamp}")
        
        # Calculate P-Factor
        ocean_dict = {
            "openness": data.ocean_normalized.openness,
            "conscientiousness": data.ocean_normalized.conscientiousness,
            "extraversion": data.ocean_normalized.extraversion,
            "agreeableness": data.ocean_normalized.agreeableness,
            "neuroticism": data.ocean_normalized.neuroticism
        }
        p_factor = calculate_p_factor(ocean_dict)
        print(f"\n Calculated P-Factor: {p_factor}")
        
        # Calculate Retention for logging (but don't store it)
        retention_val, phase, _ = calculate_retention(p_factor, days=0)
        print(f" Calculated Retention (Day 0): {retention_val}")
        
        # Calculate Confidence based on retention
        conf_val, conf_label = calculate_confidence(retention_val) 
        print(f"   Confidence: {conf_val} ({conf_label})")
        
        recon_msg = reconstruct_memory(retention_val)
        print(f"   Reconstruction: {recon_msg}")
        
        # Urgency Calculation (Vk)
        urgency_val, urgency_msg = calculate_urgency(0.8, 2.0, 5.0)
        print(f"   Urgency: {urgency_msg}")
        
        # Priority Calculation 
        urgency_normalized = min(1.0, urgency_val)
        prio_val, prio_msg = calculate_priority(p_factor, urgency_normalized, retention_val)
        print(f"   Priority: {prio_msg}")

        # Trigger initial linguistic generation
        base_memory = "Initial data ingestion and personality assessment."
        response_text = generate_npc_response(base_memory, conf_label, phase, retention_val)

        # document for MongoDB
        document = {
            "report_id": data.report_id,
            "timestamp": data.timestamp,
            "p_factor": p_factor,
            "priority_mock": prio_val,
            "ocean_scores": data.ocean_scores.dict(),
            "ocean_normalized": data.ocean_normalized.dict(),
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "last_linguistic_response": response_text,
            "confidence_at_generation": conf_val,
            "retention_at_generation": retention_val,
            "generation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        result = ocean_collection.insert_one(document)
        
        print(f"\n SAVED TO MONGODB")
        print(f"   MongoDB ID: {result.inserted_id}")
        print("=" * 60 + "\n")
        
        return {
            "success": True,
            "message": "OCEAN scores saved successfully",
            "data": {
                "mongodb_id": str(result.inserted_id),
                "report_id": data.report_id,
                "p_factor": p_factor
            }
        }
    except Exception as e:
        print(f"\n ERROR SAVING TO MONGODB: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulate-memory")
async def simulate_memory(p_factor: float, days: float, strength: float = 2.8):

    try:
        ret_val, phase, _ = calculate_retention(p_factor)
        ret_msg = (ret_val, phase)
        conf_val, conf_label = calculate_confidence(0.5) 
        
        return {
            "success": True,
            "inputs": {
                "p_factor": p_factor,
                "days_passed": days,
                "memory_strength": strength
            },
            "results": {
                "retention_msg": ret_msg,
                "confidence_score": conf_val,
                "confidence_label": conf_label
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-ocean-scores/{report_id}")
async def get_ocean_scores(report_id: str):
    
    try:
        print(f"\n🔍 Searching for report_id: {report_id}")
        
        result = ocean_collection.find_one({"report_id": report_id})
        
        if not result:
            print(f" Report not found: {report_id}\n")
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Convert ObjectId to string
        result["_id"] = str(result["_id"])
        
        print(f" Found report: {report_id}")
        print(f"   Normalized scores: O={result['ocean_normalized']['openness']:.3f}, "
              f"C={result['ocean_normalized']['conscientiousness']:.3f}, "
              f"E={result['ocean_normalized']['extraversion']:.3f}, "
              f"A={result['ocean_normalized']['agreeableness']:.3f}, "
              f"N={result['ocean_normalized']['neuroticism']:.3f}\n")
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/all-ocean-scores")
async def get_all_ocean_scores():
    
    try:
        results = list(ocean_collection.find().sort("saved_at", -1))
        
        # Convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
        
        print(f"\n Retrieved {len(results)} OCEAN score records from MongoDB\n")
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        print(f" Error: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/delete-ocean-scores/{report_id}")
async def delete_ocean_scores(report_id: str):
    
    try:
        result = ocean_collection.delete_one({"report_id": report_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Report not found")
        
        print(f" Deleted report: {report_id}\n")
        
        return {
            "success": True,
            "message": f"Report {report_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save-task")
async def save_task(task: TaskItem):
    
    try:
        task_dict = task.dict()
        task_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        
        task_dict["importance_kk"] = float(task_dict["importance_kk"])
        task_dict["required_time_trk"] = float(task_dict["required_time_trk"])
        task_dict["available_time_tak"] = float(task_dict["available_time_tak"])
        
        result = tasks_collection.insert_one(task_dict)
        print(f" Task Assigned: {task.task_name} | ID: {result.inserted_id}")
        
        return {
            "success": True,
            "message": "Task saved successfully",
            "task_id": str(result.inserted_id)
        }
    except Exception as e:
        print(f" Error saving task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-tasks/{report_id}")
async def get_tasks(report_id: str):
    
    try:
        tasks = list(tasks_collection.find({"report_id": report_id}).sort("created_at", -1))
        for t in tasks:
            t["_id"] = str(t["_id"])
        
        return {
            "success": True,
            "tasks": tasks
        }
    except Exception as e:
        print(f" Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-npc-response/{report_id}")
async def generate_response(report_id: str, base_memory: str = "The last assigned task"):
    
    try:
        report = ocean_collection.find_one({"report_id": report_id}, sort=[("saved_at", -1)])
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Calculate current retention
        start_time = datetime.fromisoformat(report["saved_at"])
        retention, debug, phase = calculate_retention_from_timestamp(report["p_factor"], start_time)
        
        # Calculate confidence
        conf_val, conf_label = calculate_confidence(retention)
        
        # Generate Linguistic Response
        response_text = generate_npc_response(base_memory, conf_label, phase, retention)
        
        update_data = {
            "last_linguistic_response": response_text,
            "confidence_at_generation": conf_val,
            "retention_at_generation": retention,
            "generation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        ocean_collection.update_one({"_id": report["_id"]}, {"$set": update_data})
        
        print(f" Generated Response for {report_id}: {response_text[:30]}...")
        
        return {
            "success": True,
            "response": response_text,
            "metadata": {
                "confidence_label": conf_label,
                "confidence_score": conf_val,
                "retention_val": retention,
                "phase": phase
            }
        }
    except Exception as e:
        print(f" Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/adk/execute-task/{report_id}")
async def execute_task_stream(report_id: str, task: str):
    
    def event_stream():
        try:
            for progress_text in execute_task_with_adk(report_id, task):
                yield f"data: {progress_text}\n\n"
        except Exception as e:
            yield f"data:  Stream Error: {str(e)}\n\n"
    
    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/api/adk/get-npc-state/{report_id}")
async def get_npc_state_for_adk(report_id: str):
    candidate = ocean_collection.find_one({"report_id": report_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="NPC not found")

    retention, _, phase = calculate_retention_from_timestamp(
        candidate["p_factor"], 
        datetime.fromisoformat(candidate["saved_at"])
    )    

    conf_val, conf_label = calculate_confidence(retention)

    active_task = tasks_collection.find_one(
        {"report_id": report_id}, 
        sort=[("created_at", -1)]
    )
    
    return {
        "retention": retention,
        "confidence": conf_val,
        "confidence_label": conf_label,
        "phase": phase,
        "p_factor": candidate["p_factor"], 
        "active_task": active_task["task_name"] if active_task else None,
        "should_struggle": retention < 0.40,
        "is_confused": retention < 0.30
    }

running_tasks = {}

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    
    try:
        from bson import ObjectId
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task["_id"] = str(task["_id"])
        
        return {
            "success": True,
            "task": task
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/start-task/{task_id}")
async def start_task_execution(task_id: str):
    
    try:
        from bson import ObjectId
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.get("status") == "running":
            return {
                "success": False,
                "message": "Task is already running"
            }
        
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "status": "running",
                    "started_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        def execute_in_background():
            try:
                execution_log = []
                for progress in execute_task_with_adk(task["report_id"], task["task_name"]):
                    execution_log.append(progress)
                    tasks_collection.update_one(
                        {"_id": ObjectId(task_id)},
                        {"$set": {"execution_log": execution_log}}
                    )
                
                tasks_collection.update_one(
                    {"_id": ObjectId(task_id)},
                    {
                        "$set": {
                            "status": "completed",
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                            "execution_log": execution_log
                        }
                    }
                )
            except Exception as e:
                # Mark as failed
                tasks_collection.update_one(
                    {"_id": ObjectId(task_id)},
                    {
                        "$set": {
                            "status": "failed",
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                            "execution_log": execution_log + [f" Error: {str(e)}"]
                        }
                    }
                )
        
        thread = threading.Thread(target=execute_in_background, daemon=True)
        thread.start()
        running_tasks[task_id] = thread
        
        return {
            "success": True,
            "message": "Task execution started",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete-task/{task_id}")
async def delete_task(task_id: str):
   
    try:
        from bson import ObjectId
        result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        print(f" Deleted task: {task_id}")
        
        return {
            "success": True,
            "message": f"Task {task_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adk/execute-task-stream/{task_id}")
async def execute_task_stream_by_id(task_id: str):

    from bson import ObjectId
    
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    def event_stream():
        try:
            if task.get("status") == "completed":
                for line in task.get("execution_log", []):
                    yield f"data: {line}\n\n"
                yield f"data:  Task completed (replaying log)\n\n"
                return
            
            # Mark task as running
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Stream live execution and collect logs
            execution_log = []
            task_desc = task.get("task_description", "")
            image_paths = task.get("uploaded_files", [])
            
            for progress_text in execute_task_with_adk(
                task["report_id"], 
                task["task_name"],
                task_description=task_desc,
                image_paths=image_paths
            ):
                execution_log.append(progress_text)
                yield f"data: {progress_text}\n\n"
            
            # Save execution log and mark as completed
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "execution_log": execution_log
                }}
            )
            print(f" Task {task_id} completed. Log saved ({len(execution_log)} lines)")
            
        except Exception as e:
            yield f"data:  Stream Error: {str(e)}\n\n"
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"status": "failed"}}
            )
    
    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
        }
    )

class AudioUrlUpdate(BaseModel):
    audio_url: str

@app.put("/api/task-audio/{task_id}")
async def save_task_audio_url(task_id: str, update: AudioUrlUpdate):

    try:
        from bson import ObjectId
        print(f" Saving audio URL for task {task_id}: {update.audio_url}")
        
        result = tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"tts_audio_url": update.audio_url}}
        )
        
        if result.matched_count == 0:
            print(f" Task {task_id} not found for audio update")
            raise HTTPException(status_code=404, detail="Task not found")
            
        print(f" Audio URL saved for task {task_id}")
        return {"success": True}
    except Exception as e:
        print(f" Error saving audio URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-task-file")
async def upload_task_file(file: UploadFile = File(...)):
    
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f" File uploaded: {file_path}")
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    
    return {
        "message": "Big Five OCEAN API with MongoDB",
        "status": "running",
        "database": "MongoDB connected",
        "endpoints": {
            "POST /api/save-ocean-scores": "Save OCEAN test results to MongoDB",
            "GET /api/get-ocean-scores/{report_id}": "Get results by report ID",
            "GET /api/all-ocean-scores": "Get all saved results",
            "DELETE /api/delete-ocean-scores/{report_id}": "Delete results by report ID",
            "POST /api/save-task": "Assign a task to an NPC",
            "GET /api/get-tasks/{report_id}": "Get all tasks for a specific NPC",
            "POST /api/generate-npc-response/{report_id}": "Generate linguistic NPC response"
        }
    }

@app.get("/health")
async def health_check():
   
    try:
        client.server_info()
        return {
            "status": "healthy",
            "mongodb": "connected",
            "database": "bigfive",
            "collection": "ocean_scores"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "mongodb": "disconnected",
            "error": str(e)
        }

@app.delete("/api/delete-agent/{report_id}")
async def delete_agent(report_id: str):
    try:
        agent_result = ocean_collection.delete_one({"report_id": report_id})
        tasks_result = tasks_collection.delete_many({"report_id": report_id})
        
        if agent_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "success": True,
            "message": f"Agent and {tasks_result.deleted_count} tasks deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n Starting FastAPI server...")
    print(" Server will run on: http://localhost:8000")
    print(" API docs available at: http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
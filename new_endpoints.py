import threading
import asyncio
from datetime import datetime, timezone

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

                tasks_collection.update_one(
                    {"_id": ObjectId(task_id)},
                    {
                        "$set": {
                            "status": "failed",
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                            "execution_log": execution_log + [f"❌ Error: {str(e)}"]
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
                yield f"data: Task completed (replaying log)\n\n"
                return
            
            for progress_text in execute_task_with_adk(task["report_id"], task["task_name"]):
                yield f"data: {progress_text}\n\n"
        except Exception as e:
            yield f"data:  Stream Error: {str(e)}\n\n"
    
    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
        }
    )

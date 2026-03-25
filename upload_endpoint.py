# File upload endpoint - Add to main.py after line 550

@app.post("/api/upload-task-file")
async def upload_task_file(file: UploadFile = File(...)):
    """
    Upload image file for task assignment
    Returns file path for storage in MongoDB
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"📁 File uploaded: {file_path}")
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

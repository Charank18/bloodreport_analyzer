# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# import os
# import uuid
# import asyncio

# from crewai import Crew, Process
# from agents import doctor
# from task import help_patients

# app = FastAPI(title="Blood Test Report Analyser")

# def run_crew(query: str, file_path: str="data/sample.pdf"):
#     """To run the whole crew"""
#     medical_crew = Crew(
#         agents=[doctor],
#         tasks=[help_patients],
#         process=Process.sequential,
#     )
    
#     result = medical_crew.kickoff({'query': query})
#     return result

# @app.get("/")
# async def root():
#     """Health check endpoint"""
#     return {"message": "Blood Test Report Analyser API is running"}

# @app.post("/analyze")
# async def analyze_blood_report(
#     file: UploadFile = File(...),
#     query: str = Form(default="Summarise my Blood Test Report")
# ):
#     """Analyze blood test report and provide comprehensive health recommendations"""
    
#     # Generate unique filename to avoid conflicts
#     file_id = str(uuid.uuid4())
#     file_path = f"data/blood_test_report_{file_id}.pdf"
    
#     try:
#         # Ensure data directory exists
#         os.makedirs("data", exist_ok=True)
        
#         # Save uploaded file
#         with open(file_path, "wb") as f:
#             content = await file.read()
#             f.write(content)
        
#         # Validate query
#         if query=="" or query is None:
#             query = "Summarise my Blood Test Report"
            
#         # Process the blood report with all specialists
#         response = run_crew(query=query.strip(), file_path=file_path)
        
#         return {
#             "status": "success",
#             "query": query,
#             "analysis": str(response),
#             "file_processed": file.filename
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")
    
#     finally:
#         # Clean up uploaded file
#         if os.path.exists(file_path):
#             try:
#                 os.remove(file_path)
#             except:
#                 pass  # Ignore cleanup errors

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from celery.result import AsyncResult

from celery_worker import run_analysis_task  # Celery task
from models import SessionLocal, AnalysisResult  # For DB result lookup

app = FastAPI(title="Blood Test Report Analyser")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Accepts a PDF and query, queues the analysis task"""
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if not query:
            query = "Summarise my Blood Test Report"

        # Queue Celery task
        task = run_analysis_task.delay(query.strip(), file_path)

        return {
            "status": "queued",
            "task_id": task.id,
            "file": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing: {str(e)}")


@app.get("/result/{task_id}")
def get_result(task_id: str):
    """Retrieve result using Celery task ID"""
    result = AsyncResult(task_id)

    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "STARTED":
        return {"status": "processing"}
    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.info)}
    elif result.state == "SUCCESS":
        return {
            "status": "completed",
            "task_id": task_id,
            "result": result.result
        }
    return {"status": result.state}


@app.get("/history")
def get_analysis_history():
    """Optional: Get past analysis results"""
    db = SessionLocal()
    records = db.query(AnalysisResult).all()
    db.close()
    return [
        {
            "id": rec.id,
            "query": rec.query,
            "file_name": rec.file_name,
            "result": rec.result
        }
        for rec in records
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

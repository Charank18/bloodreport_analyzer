from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)
@celery_app.task
def run_analysis_task(query: str, file_path: str):
    try:
        from crewai import Crew, Process
        from agents import doctor
        from task import help_patients
        from models import SessionLocal, AnalysisResult

        crew = Crew(agents=[doctor], tasks=[help_patients], process=Process.sequential)
        result = crew.kickoff({'query': query})

        db = SessionLocal()
        record = AnalysisResult(file_name=file_path, query=query, result=str(result))
        db.add(record)
        db.commit()
        db.refresh(record)
        db.close()

        return record.result

    except Exception as e:
        print("TASK FAILED:", str(e))
        return f"Failed: {str(e)}"


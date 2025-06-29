run this command : $ celery -A celery_worker worker --loglevel=info --pool=solo  and run this uvicorn main:app --reload in two separate terminals

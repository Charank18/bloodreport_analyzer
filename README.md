run this command : $ celery -A celery_worker worker --loglevel=info --pool=solo  and run this command : uvicorn main:app --reload simulataneously in two separate terminals

changes made: 
added openai key for inference and modified dependencies errors


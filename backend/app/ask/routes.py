# app/ask/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ask.tasks import process_question
from app.database.redis_client import redis_client
import json
import uuid

router = APIRouter()

class AskRequest(BaseModel):
    user_id: str
    question: str

@router.post("/")
def ask_question(body: AskRequest):
    """
    Accepts JSON: {"user_id": "<str>", "question": "<str>"}
    Creates a Celery task and stores initial task metadata in Redis.
    Returns task_id immediately.
    """
    # quickly validate
    if not body.user_id or not body.question:
        raise HTTPException(status_code=400, detail="user_id and question required")

    # enqueue the Celery task
    async_result = process_question.apply_async(args=(body.user_id, body.question))
    task_id = async_result.id

    # initialize task metadata in Redis
    task_key = f"task:{task_id}"
    redis_client.hset(task_key, mapping={"status": "pending", "user_id": body.user_id})
    redis_client.expire(task_key, int(86400))  # same as ANSWER_TTL

    return {"task_id": task_id}

@router.get("/task/{task_id}")
def task_status(task_id: str):
    task_key = f"task:{task_id}"
    info = redis_client.hgetall(task_key)
    if not info:
        raise HTTPException(status_code=404, detail="Task not found")
    if info.get("status") == "done":
        result_key = info.get("result_key")
        answer = redis_client.get(result_key)
        return {"status": "done", "answer": answer}
    if info.get("status") == "error":
        return {"status": "error", "error": info.get("error")}
    return {"status": info.get("status", "processing")}

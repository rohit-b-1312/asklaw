# app/ask/tasks.py
import os
import json
from app.worker import celery_app
from app.semantic.vector_store import search_similar
from app.ask.llm import generate_answer
from app.database.redis_client import redis_client
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
ANSWER_TTL = int(os.getenv("ANSWER_TTL", 86400))  # 24 hours

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3, acks_late=True)
def process_question(self, user_id: str, question: str):
    """
    Celery task that:
      - records task status in Redis (task:{task_id})
      - runs semantic search (Qdrant) to fetch top documents
      - calls LLM to produce an answer
      - stores the answer in Redis and marks task done
    """
    task_id = self.request.id
    task_key = f"task:{task_id}"
    try:
        # mark as processing
        redis_client.hset(task_key, mapping={"status": "processing", "user_id": user_id})
        redis_client.expire(task_key, ANSWER_TTL)

        # Quick de-dup check: try to fetch cached top-k by question text (optional)
        question_key = f"question_cache:{user_id}:{hash(question)}"
        cached = redis_client.get(question_key)
        if cached:
            answer = cached
            meta = {"cached": True}
            result_key = f"result:{task_id}"
            redis_client.set(result_key, answer, ex=ANSWER_TTL)
            redis_client.hset(task_key, mapping={"status": "done", "result_key": result_key})
            redis_client.expire(task_key, ANSWER_TTL)
            return {"answer": answer, "metadata": meta, "cached": True}

        # 1) retrieve top documents from Qdrant
        top_k = int(os.getenv("TOP_K", 5))
        docs, meta = search_similar(question, top_k=top_k)

        # 2) ask LLM to generate answer with context
        answer = generate_answer(question=question, context="\n\n".join(docs))

        # 3) store result
        result_key = f"result:{task_id}"
        redis_client.set(result_key, answer, ex=ANSWER_TTL)
        # optionally cache question-level answer for short period
        redis_client.set(question_key, answer, ex=int(os.getenv("QUESTION_CACHE_TTL", 3600)))

        # 4) mark task done
        redis_client.hset(task_key, mapping={"status": "done", "result_key": result_key})
        redis_client.expire(task_key, ANSWER_TTL)

        return {"answer": answer, "metadata": meta, "cached": False}
    except Exception as exc:
        logger.exception("process_question failed")
        redis_client.hset(task_key, mapping={"status": "error", "error": str(exc)})
        redis_client.expire(task_key, ANSWER_TTL)
        raise

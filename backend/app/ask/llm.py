# app/ask/llm.py
import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MAX_PROMPT_CHARS = int(os.getenv("MAX_PROMPT_CHARS", 4000))

# Lazy import Groq (only if API key present)
client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None

def _truncate_context(context: str, max_chars: int = MAX_PROMPT_CHARS) -> str:
    if not context:
        return ""
    return context if len(context) <= max_chars else context[-max_chars:]

def generate_answer(question: str, context: str) -> str:
    """
    Produce an answer string. If Groq client available, call the chat model.
    Otherwise, return a simple synthesized answer using the top documents (fallback).
    """
    ctx = _truncate_context(context)

    if client:
        # build a concise prompt
        prompt = f"""You are a helpful assistant. Use the context to answer the question concisely.
Question: {question}

Context:
{ctx}

Answer concisely, mention sources if present, and include a short "Confidence" line (low/medium/high).
Disclaimer: This is not legal advice.
"""
        chat = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        # depending on groq client response shape
        try:
            return chat.choices[0].message.content
        except Exception:
            # best-effort fallback:
            return str(chat)
    else:
        # fallback: return merged context + short answer stub
        if not ctx:
            return "I don't have context to answer that. (No documents indexed.)"
        # attempt a short synthetic answer
        top_lines = ctx.splitlines()[:5]
        short_ctx = "\n".join(top_lines)
        return f"Based on these documents:\n{short_ctx}\n\nAnswer (short): {question}\nConfidence: medium\nDisclaimer: Not legal advice."

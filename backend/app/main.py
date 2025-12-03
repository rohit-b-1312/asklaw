from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()
from app.ask.routes import router as ask_router
from app.auth.routes import router as auth_router

# Prometheus
from prometheus_client import Counter, Histogram
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        resp_time = time.time() - start
        try:
            REQUEST_LATENCY.labels(request.method, request.url.path).observe(resp_time)
            REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
        except Exception:
            pass
        return response

app = FastAPI(title="AskLaw Backend")
app.add_middleware(MetricsMiddleware)

# Mount Prometheus ASGI app at /metrics
app.mount("/metrics", make_asgi_app())

app.include_router(ask_router, prefix="/api/ask", tags=["Ask"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])


@app.get("/")
def home():
    return {"message": "AskLaw API is running"}

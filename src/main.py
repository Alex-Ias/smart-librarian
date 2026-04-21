import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.api.assistant_service import build_assistant_response
from src.api.constants import APP_TITLE, APP_VERSION
from src.api.schemas import AssistantRequest, AssistantResponse
from src.api.settings import settings
from src.vector_store.embed_and_store import ensure_indexed

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    ensure_indexed()
    yield


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health() -> dict:
    return {
        "status": "ok",
        "service": APP_TITLE.lower().replace(" ", "-"),
        "version": APP_VERSION,
    }


@app.post("/chat", response_model=AssistantResponse, tags=["Assistant"])
async def chat(request: AssistantRequest) -> AssistantResponse:
    return await build_assistant_response(request)
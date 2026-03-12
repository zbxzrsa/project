from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.database import init_db
from backend.core.exceptions import AppException
from backend.core.logging import setup_logging, logger
from backend.api.v1 import api_router
from backend.core.websocket import ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    setup_logging()
    await init_db()
    logger.info("Application started successfully")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "detail": "An unexpected error occurred",
        },
    )


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

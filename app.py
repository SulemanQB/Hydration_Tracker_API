import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from a2wsgi import WSGIMiddleware
from src.controllers import user_controller, hydration_tracker_controller
from fastapi.openapi.utils import get_openapi
from src.app import frontend_app
from src.middleware.rate_limiter import RateLimiter
from config.settings import settings
import uvicorn

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("hydration_tracker")

api = FastAPI(
    title="Hydration Tracker API",
    description="A simple API with MongoDB to track your daily hydration intake.",
    version="1.0",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:443",
    "https://localhost",
    "https://localhost:8000",
    "https://localhost:443",
    "https://hydration-tracker-kvgl74sgpa-rj.a.run.app",
    "https://hydration-tracker-kvgl74sgpa-rj.a.run.app:8000",
    "http://hydration-tracker-kvgl74sgpa-rj.a.run.app"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.RATE_LIMIT_ENABLED:
    api.add_middleware(
        RateLimiter,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
    )

api.mount("/app", WSGIMiddleware(frontend_app))

@api.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@api.get("/")
def hello_world():
    return {"Hello": "World"}

api.include_router(user_controller.router)
api.include_router(hydration_tracker_controller.router)

def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    
    openapi_schema = get_openapi(
        title="Hydration Tracker API",
        version="1.0",
        routes=api.routes,
    )
    
    openapi_schema["info"] = {
        "title": "Hydration Tracker API",
        "version": "1.0",
        "description": "A simple API with MongoDB to track your daily hydration intake.",
        "contact": {
            "name": "Gabriel Coelho",
            "url": "gabrielfmcoelho.github.io",
            "email": "gabrielcoelho09gc@gmail.com"
        }
    }
    
    api.openapi_schema = openapi_schema
    return api.openapi_schema

api.openapi = custom_openapi

if __name__ == "__main__": 
    logger.info("Starting Hydration Tracker API")
    
    if settings.SSL_ENABLED and settings.SSL_CERT_PATH and settings.SSL_KEY_PATH:
        logger.info("SSL enabled - starting with HTTPS")
        uvicorn.run(
            "app:api",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_DEBUG,
            ssl_keyfile=settings.SSL_KEY_PATH,
            ssl_certfile=settings.SSL_CERT_PATH
        )
    else:
        logger.info("SSL disabled - starting with HTTP only")
        uvicorn.run(
            "app:api",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_DEBUG
        )
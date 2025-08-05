import logging
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from src.controllers import user_controller, hydration_tracker_controller
from fastapi.openapi.utils import get_openapi
from src.app import frontend_app
from src.middleware.rate_limiter import RateLimiter
from config.settings import settings
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("hydration_tracker")

# Initialize FastAPI app
api = FastAPI(
    title="Hydration Tracker API",
    description="A simple API with MongoDB to track your daily hydration intake.",
    version="1.0",
)

# CORS configuration
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

# Add middlewares
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware if enabled
if settings.RATE_LIMIT_ENABLED:
    api.add_middleware(
        RateLimiter,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
    )

# Mount Flask app for frontend
api.mount("/app", WSGIMiddleware(frontend_app))

# Global error handler
@api.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

# Validation error handler
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

# Include routers
api.include_router(user_controller.router)
api.include_router(hydration_tracker_controller.router)

# Custom OpenAPI schema
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
    
    # Check if SSL is enabled
    if settings.SSL_ENABLED and settings.SSL_CERT_PATH and settings.SSL_KEY_PATH:
        logger.info("SSL enabled - starting with HTTPS")
        uvicorn.run(
            api,
            host="0.0.0.0",
            port=8000,
            reload=True,
            ssl_keyfile=settings.SSL_KEY_PATH,
            ssl_certfile=settings.SSL_CERT_PATH
        )
    else:
        logger.info("SSL disabled - starting with HTTP only")
        uvicorn.run(
            api,
            host="0.0.0.0",
            port=8000,
            reload=True
        )
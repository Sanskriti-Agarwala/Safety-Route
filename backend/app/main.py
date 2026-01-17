from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import route, report, sos, safety

app = FastAPI(
    title="Safety Route API",
    description="AI-assisted navigation backend prioritizing user safety over fastest routes",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route planning APIs
app.include_router(
    route.router,
    prefix="/routes",
    tags=["Routes"]
)

# Register report / safety / incident APIs
app.include_router(
    report.router,
    prefix="/reports",
    tags=["Reports"]
)

app.include_router(
    sos.router,
    prefix="/sos",
    tags=["SOS"]
)

# Register safety analysis API
app.include_router(
    safety.router,
    prefix="/safety",
    tags=["Safety"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Safety Route API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Safety Route backend is running"
    }
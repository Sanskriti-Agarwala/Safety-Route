from fastapi import FastAPI
from app.api.routes import route, report,sos

app = FastAPI(
    title="Safety Route API",
    description="AI-assisted navigation backend prioritizing user safety over fastest routes",
    version="1.0.0"
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

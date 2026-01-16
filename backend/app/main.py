from fastapi import FastAPI
from app.api.routes import report

app = FastAPI(
    title="Safety Route API",
    description="AI-assisted navigation backend prioritizing user safety over fastest routes",
    version="1.0.0"
)

app.include_router(report.router)


@app.get("/")
async def root():
    return {
        "message": "Safety Route API is running",
        "status": "healthy",
        "version": "1.0.0"
    }
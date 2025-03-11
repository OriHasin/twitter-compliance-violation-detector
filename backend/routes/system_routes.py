from fastapi import APIRouter

# Create system router for health checks and system-level endpoints
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "Twitter Compliance Violation Service"}
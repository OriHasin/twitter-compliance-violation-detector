from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from routes import policy_router, tweet_router, system_router
from database import create_tables
from config import UPLOAD_DIR



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and create directories
    await create_tables()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print("✅ Application initialized successfully")
    
    yield  # Application runs here
    
    # Shutdown: cleanup (if needed)
    pass



app = FastAPI(title="Twitter Compliance Violation Service", lifespan=lifespan)

# Include API routers
app.include_router(policy_router)
app.include_router(tweet_router)
app.include_router(system_router)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from routes import policy_router, tweet_router, system_router
from websocket_manager import websocket_app

app = FastAPI(title="Twitter Compliance Violation Service")

# Include API routers
app.include_router(policy_router)
app.include_router(tweet_router)
app.include_router(system_router)

# Include WebSocket endpoint for live updates
app.add_websocket_route("/ws", websocket_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
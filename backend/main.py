from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.timers import router as timers_router
import os

app = FastAPI(title="Time Tracking App")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Include routes
app.include_router(timers_router, prefix="/api", tags=["timers"])

@app.get("/")
def read_root():
    return {"message": "Time Tracking App API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

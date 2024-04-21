from fastapi import FastAPI
from summarization_service import router as summarize_router
from auth_service import router as auth_router
from feature_tracking_service import router as feature_tracking_router
from database import create_user_db

app = FastAPI()

# This creates the users database in sqllite if it doesn't exist
@app.on_event("startup")
async def startup_event():
    create_user_db()

@app.get("/")
async def root():
    return {"message": "Server Started!"}

app.include_router(summarize_router, prefix='/summarize', tags=['Summarization'])
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(feature_tracking_router, prefix='/feature', tags=['Tracking'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
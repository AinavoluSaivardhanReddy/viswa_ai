from fastapi import FastAPI
from summarization_service import router as summarize_router
from auth_service import router as auth_router
from database import create_user_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_user_db()

@app.get("/")
async def root():
    return {"message": "Server Started!"}

app.include_router(summarize_router, prefix='/summarize', tags=['Summarization'])
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
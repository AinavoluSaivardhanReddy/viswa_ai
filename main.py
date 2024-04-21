from fastapi import FastAPI
from summarization_service import router as summarize_router
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Server Started!"}

app.include_router(summarize_router, prefix='/summarize', tags=['Summarization'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from transformers import pipeline
from validation_service import validate_user

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

router = APIRouter()

class QueryModel(BaseModel):
    txt:str

def summarize(text:str):
    response = summarizer(text, max_length=500, min_length=30, do_sample=False)
    return response[0]['summary_text']

@router.post("/")
# We are usng dependency injection(Depends) here to validate the use session and subscription validation
async def encode_query(request: QueryModel, user = Depends(validate_user)):
    try:
        response = summarize(request.txt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
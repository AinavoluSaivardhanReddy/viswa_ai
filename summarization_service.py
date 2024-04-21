from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from transformers import pipeline
from validation_service import validate_user
from feature_tracking_service import track_feature_usage

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

router = APIRouter()

class QueryModel(BaseModel):
    txt:str

def summarize(text:str):
    response = summarizer(text, max_length=500, min_length=30, do_sample=False)
    return response[0]['summary_text']

@router.post("/")
@track_feature_usage("Summarize")
async def encode_query(request: QueryModel, user = Depends(validate_user)):
    '''
    We are using dependency injection(Depends) here to validate the user session and subscription validation
    By using @track_feature_usage decorator we can track the feature usage for this function
    '''
    try:
        response = summarize(request.txt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
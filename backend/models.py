from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class SentimentResponse(BaseModel):
    sentiment: Literal['happy', 'sad', 'tired']
    generated_at: datetime = Field(default_factory=datetime.utcnow)

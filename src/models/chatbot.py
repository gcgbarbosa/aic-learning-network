from datetime import datetime
from pydantic import BaseModel, Field


class ChatbotRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the chatbot")
    name: str = Field(..., description="Chatbot name")
    created: datetime = Field(..., description="Timestamp when the record was created")
    updated: datetime = Field(..., description="Timestamp when the record was updated")

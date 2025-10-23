
from datetime import datetime
from pydantic import BaseModel, Field


class MessageRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the message")
    role: str = Field(..., description="Role of the sender (user, assistant, system)")
    content: str = Field(..., description="Message content")
    interaction_id: str = Field(..., description="Identifier of the related chatbot interaction")
    timestamp: datetime = Field(..., description="Time when the message was created")

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class FeedbackRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the message")

    interaction_id: str = Field(..., description="Identifier of the related chatbot interaction")

    feedback: dict[str, Any] = Field(..., description="Json string with the feedback")

    created: datetime = Field(..., description="Timestamp when the record was created")
    updated: datetime = Field(..., description="Timestamp when the record was last updated")

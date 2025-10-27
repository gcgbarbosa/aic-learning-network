from datetime import datetime

from pydantic import BaseModel, Field


class ChatbotInteractionRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the chatbot interaction")

    elapsed_time: int = Field(..., description="Time elapsed for the interaction in seconds")
    is_finished: bool = Field(..., description="Indicates if the interaction is finished")

    user_name: str = Field(..., description="The name of the person who took the test")
    session_id: str = Field(..., description="The session id the user chose")
    interaction_settings_id: str = Field(..., description="Identifier for the related interaction settings")

    created: datetime = Field(..., description="Timestamp when the record was created")
    updated: datetime = Field(..., description="Timestamp when the record was updated")

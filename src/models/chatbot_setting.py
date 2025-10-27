from datetime import datetime
from pydantic import BaseModel, Field


class ChatbotSettingsRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the chatbot settings record")

    system_message: str = Field(..., description="System message that defines the chatbot’s behavior")
    chatbot_id: str = Field(..., description="Identifier of the chatbot associated with these settings")
    interaction_settings_id: str = Field(..., description="Identifier for the related interaction settings")

    created: datetime = Field(..., description="Timestamp when the record was created")
    updated: datetime = Field(..., description="Timestamp when the record was last updated")

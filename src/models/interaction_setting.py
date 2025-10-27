from datetime import datetime
from pydantic import BaseModel, Field


class InteractionSettingsRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the interaction settings record")

    system_prompt: str = Field(..., description="System prompt defining the assistant behavior for this interaction")
    name: str = Field(..., description="Name of the interaction settings profile")

    created: datetime = Field(..., description="Timestamp when the record was created")
    updated: datetime = Field(..., description="Timestamp when the record was last updated")

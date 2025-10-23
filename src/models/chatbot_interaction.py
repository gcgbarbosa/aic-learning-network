from datetime import datetime

from pydantic import BaseModel, Field

from .chatbot import ChatbotRecord
from .message import MessageRecord


class ChatbotInteractionRecord(BaseModel):
    id: str = Field(..., description="Unique identifier of the chatbot interaction")
    elapsed_time: int = Field(..., description="Time elapsed for the interaction in seconds")
    position: int = Field(..., description="Position or ordering of the interaction")
    created: datetime = Field(..., description="Datetime when the interaction was created (UTC)")
    updated: datetime = Field(..., description="Datetime when the interaction was last updated (UTC)")
    is_finished: bool = Field(..., description="Indicates if the interaction is finished")

    user_id: str = Field(..., description="Identifier of the user")
    chatbot_id: str = Field(..., description="The id of the chatbot used")

    chatbot: ChatbotRecord | None = Field(default=None, description="The chatbot used")
    messages: list[MessageRecord] | None = Field(default=None, description="Messages exchanged during interaction")

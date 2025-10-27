from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)

from src.models import MessageRecord


class MessageAdapter:
    @staticmethod
    def adapt_message(message: MessageRecord, system_message: str | None = None):
        if message.role == "user":
            if system_message:
                return ModelRequest(
                    parts=[
                        SystemPromptPart(content=system_message),
                        UserPromptPart(content=message.content),
                    ]
                )
            return ModelRequest(parts=[UserPromptPart(content=message.content)])
        if message.role == "assistant":
            return ModelResponse(parts=[TextPart(content=message.content)])

        raise ValueError(f"Unknown message role: {message.role}")

    @staticmethod
    def adapt_message_list(messages: list[MessageRecord], system_message: str | None = None):
        adapted_messages = []

        for key in range(len(messages)):
            message = messages[key]

            if key == 0:
                adapted_messages.append(MessageAdapter.adapt_message(message, system_message))
            else:
                adapted_messages.append(MessageAdapter.adapt_message(message))

        return adapted_messages

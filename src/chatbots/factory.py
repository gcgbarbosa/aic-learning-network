from typing import Callable, TypeVar, Type

from src.models import ChatbotRecord
from src.chatbots.base_chatbot import BaseChabot

from loguru import logger

T = TypeVar("T", bound=BaseChabot)


class ChatbotFactory:
    _registry: dict[str, type[BaseChabot]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(chatbot_cls: type[T]) -> type[T]:
            logger.info(f"Registering chatbot '{name}, class={chatbot_cls}'")

            cls._registry[name] = chatbot_cls

            return chatbot_cls

        return decorator

    @classmethod
    def is_database_in_sync(cls, chatbots: list[ChatbotRecord]):
        for chatbot in ChatbotFactory._registry.keys():
            if chatbot not in [c.id for c in chatbots]:
                raise ValueError(f"Chatbot '{chatbot}' is registered but not in database")

        logger.info("ChatbotFactory is in sync with database")

    @classmethod
    def get(cls, name: str, *args, **kwargs) -> BaseChabot:
        """Retrieve and instantiate a registered chatbot by name."""
        try:
            chatbot_cls = cls._registry[name]
        except KeyError:
            raise ValueError(f"Chatbot '{name}' is not registered")

        logger.info(f"Instantiating chatbot '{name}' with args={args}, kwargs={kwargs}")
        return chatbot_cls(*args, **kwargs)

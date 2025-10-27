from src.chatbots.base_chatbot import BaseChabot
from src.chatbots.factory import ChatbotFactory
from src.chatbots.message_adapter import MessageAdapter
from src.models.chatbot_interaction import ChatbotInteractionRecord
from src.models.chatbot_setting import ChatbotSettingsRecord
from src.models.interaction_setting import InteractionSettingsRecord
from src.models.message import MessageRecord
from src.pocketbase_db import PocketBaseDB
import os

from loguru import logger


class FlowManager:
    def __init__(self):
        self._db = PocketBaseDB()

        DEFAULT_SETTING_ID = os.getenv("DEFAULT_SETTING_ID")
        if DEFAULT_SETTING_ID is None:
            raise ValueError("DEFAULT_SETTING_ID environment variable is not set.")
        self._default_setting_id = DEFAULT_SETTING_ID

        CHATBOT_IDS = os.getenv("CHATBOT_IDS")
        if CHATBOT_IDS is None:
            raise NotImplementedError("Multiple chatbot IDs are not supported yet.")
        self._chatbot_ids = CHATBOT_IDS.split(",")

        self._chatbots = {id: ChatbotFactory.get("chatbot00000003") for id in self._chatbot_ids}

        self._interaction_id = "ttvxe4qk4erlw4a"

        self._all_messages = self.get_all_messages()

        self._chatbot_messages = {}

        for id, chatbot in self._chatbots.items():
            messages = [m for m in self._all_messages if m.chatbot_id == id or not m.chatbot_id]

            adapted_messages = MessageAdapter.adapt_message_list(messages)

            chatbot.set_history(adapted_messages)
            logger.info(f"Set history for chatbot ID '{id}' with {len(adapted_messages)} messages.")

            self._chatbot_messages[id] = messages

        logger.info(f"Initialized FlowManager with chatbots: {self._chatbot_ids}")

    def get_chatbot_ids(self) -> list[str]:
        return self._chatbot_ids

    def get_interaction(self) -> ChatbotInteractionRecord:
        return self._db.get_chatbot_interaction(self._interaction_id)

    def get_default_settings_id(self) -> str:
        return self._default_setting_id

    def get_all_messages(self) -> list[MessageRecord]:
        return self._db.list_messages_by_interaction(self._interaction_id)

    def get_chatbot_01(self) -> tuple[str, BaseChabot, list[MessageRecord]]:
        chatbot = self._chatbots.get(self._chatbot_ids[0])
        messages = self._chatbot_messages.get(self._chatbot_ids[0], [])

        if chatbot is None:
            raise ValueError(f"Chatbot with ID '{self._chatbot_ids[0]}' not found.")

        return self._chatbot_ids[0], chatbot, messages

    def get_chatbot_02(self) -> tuple[str, BaseChabot, list[MessageRecord]]:
        chatbot = self._chatbots.get(self._chatbot_ids[1])
        messages = self._chatbot_messages.get(self._chatbot_ids[1], [])

        if chatbot is None:
            raise ValueError(f"Chatbot with ID '{self._chatbot_ids[1]}' not found.")

        return self._chatbot_ids[1], chatbot, messages

    def get_chatbot_03(self) -> tuple[str, BaseChabot, list[MessageRecord]]:
        chatbot = self._chatbots.get(self._chatbot_ids[2])
        messages = self._chatbot_messages.get(self._chatbot_ids[2], [])

        if chatbot is None:
            raise ValueError(f"Chatbot with ID '{self._chatbot_ids[2]}' not found.")

        return self._chatbot_ids[2], chatbot, messages

    def create_interaction(self, user_name: str, session_id: str) -> None:
        interactions = self._db.list_chatbot_interactions_by_session(session_id=session_id)

        if len(interactions) > 0:
            raise ValueError(f"An interaction for session_id '{session_id}' already exists.")

        self._db.create_chatbot_interaction(user_name, session_id)

    def list_settings(self) -> list[InteractionSettingsRecord]:
        return self._db.list_interaction_settings()

    def get_default_setting(self) -> InteractionSettingsRecord:
        setting = self._db.get_interaction_setting(self._default_setting_id)

        if setting is None:
            raise ValueError(f"Interaction setting with ID '{self._default_setting_id}' not found.")

        return setting

    def get_interaction_and_chatbot_settings(
        self, interaction_setting_id: str
    ) -> tuple[InteractionSettingsRecord, dict[str, ChatbotSettingsRecord]]:
        interaction_settings = self._db.get_interaction_setting(interaction_setting_id)

        if interaction_settings is None:
            raise ValueError(f"Interaction setting with ID '{interaction_setting_id}' not found.")

        chatbot_settings = self._db.get_chatbot_settings(interaction_settings_id=interaction_setting_id)

        chatbot_settings_dict = {b.chatbot_id: b for b in chatbot_settings}

        return interaction_settings, chatbot_settings_dict

    def change_interaction_setting(self, interaction_settings_id: str):
        self._db.update_chatbot_interaction(self._interaction_id, interaction_settings_id=interaction_settings_id)

    def save_user_message(self, content: str) -> None:
        logger.debug(f"Saving user message: {content}")

        self._db.insert_message(role="user", content=content, interaction_id=self._interaction_id)

    def save_assistant_message(self, content: str, chatbot_id: str) -> None:
        logger.debug(f"Saving assistant message for chatbot ID '{chatbot_id}': {content}")

        self._db.insert_message(
            role="assistant", content=content, chatbot_id=chatbot_id, interaction_id=self._interaction_id
        )

    def create_interaction_settings(self, name: str, system_prompt: str, chatbot_settings: list[dict]):
        setting = self._db.create_interaction_settings(name, system_prompt, chatbot_settings)

        logger.info(f"Created interaction [{name}] settings with ID '{setting.id}'")


if __name__ == "__main__":
    # Create an instance of AuthManager
    fm = FlowManager()

    # print(fm.list_settings())

    # fm.create_interaction_settings(
    #     name="Test Interaction Settings",
    #     system_prompt="This is a test system prompt.",
    #     chatbot_settings=[
    #         {"chatbot_id": "chatbot00000001", "system_message": "System message for chatbot 1"},
    #         {"chatbot_id": "chatbot00000002", "system_message": "System message for chatbot 2"},
    #         {"chatbot_id": "chatbot00000003", "system_message": "System message for chatbot 2"},
    #     ],
    # )

    # print(fm.get_default_setting())

    # print(fm.get_all_messages())

    # print(fm.get_chatbot_01())

    print(fm.get_interaction_and_chatbot_settings("default00000000"))

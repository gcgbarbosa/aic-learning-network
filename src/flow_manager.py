from src.chatbots.base_chatbot import BaseChabot
from src.chatbots.factory import ChatbotFactory
from src.models.interaction_setting import InteractionSettingsRecord
from src.pocketbase_db import PocketBaseDB
import os

from loguru import logger


class FlowManager:
    def __init__(self):
        self.db = PocketBaseDB()

        DEFAULT_SETTING_ID = os.getenv("DEFAULT_SETTING_ID")
        if DEFAULT_SETTING_ID is None:
            raise ValueError("DEFAULT_SETTING_ID environment variable is not set.")
        self.default_setting_id = DEFAULT_SETTING_ID

        CHATBOT_IDS = os.getenv("CHATBOT_IDS")
        if CHATBOT_IDS is None:
            raise NotImplementedError("Multiple chatbot IDs are not supported yet.")
        self.chatbot_ids = CHATBOT_IDS.split(",")

        self.chatbots = {id: ChatbotFactory.get("chatbot00000003") for id in self.chatbot_ids}

        # TODO: load messages

        logger.info(f"Initialized FlowManager with chatbots: {self.chatbot_ids}")

    def get_chatbot_01(self) -> BaseChabot:
        chatbot = self.chatbots.get(self.chatbot_ids[0])

        if chatbot is None:
            raise ValueError(f"Chatbot with ID '{self.chatbot_ids[0]}' not found.")

        return chatbot

    def get_chatbot_02(self):
        chatbot = self.chatbots.get(self.chatbot_ids[1])

        if chatbot is None:
            raise ValueError(f"Chatbot with ID '{self.chatbot_ids[1]}' not found.")

        return chatbot

    def get_chatbot_03(self):
        chatbot = self.chatbots.get(self.chatbot_ids[2])

        if chatbot is None:
            raise ValueError(f"Chatbot with ID '{self.chatbot_ids[2]}' not found.")

        return chatbot

    def create_interaction(self, user_name: str, session_id: str) -> None:
        interactions = self.db.list_chatbot_interactions_by_session(session_id=session_id)

        if len(interactions) > 0:
            raise ValueError(f"An interaction for session_id '{session_id}' already exists.")

        self.db.create_chatbot_interaction(user_name, session_id)

    def list_settings(self) -> list[InteractionSettingsRecord]:
        return self.db.list_interaction_settings()

    def get_default_setting(self) -> InteractionSettingsRecord:
        setting = self.db.get_interaction_setting(self.default_setting_id)

        if setting is None:
            raise ValueError(f"Interaction setting with ID '{self.default_setting_id}' not found.")

        return setting


if __name__ == "__main__":
    # Create an instance of AuthManager
    fm = FlowManager()

    settings = fm.list_settings()
    # print(settings)

    print(fm.get_default_setting())

import os

from pocketbase import PocketBase
from pocketbase.stores.base_auth_store import BaseAuthStore

from src.models import (
    ChatbotRecord,
    ChatbotInteractionRecord,
    MessageRecord,
    ChatbotSettingsRecord,
    InteractionSettingsRecord,
    interaction_setting,
)

from typing import overload

from loguru import logger

from src.models.feedback import FeedbackRecord


class PocketBaseDB:
    def __init__(self, token: str | None = None, email: str | None = None, password: str | None = None):
        server = os.getenv("POCKETBASE_URL")

        if not server:
            raise ValueError("POCKETBASE_URL environment variable is not set")

        # self.client = PocketBase(server)

        if email and password:
            logger.info("Authenticating with provided email and password")

            self.client = PocketBase(server)
            self.client.collection("users").auth_with_password(email, password)
        elif token:
            logger.info("Authenticating with provided token")

            auth = BaseAuthStore(base_token=token)
            self.client = PocketBase(server, auth_store=auth)
        else:
            logger.info("Authenticating with admin credentials")

            self.client = PocketBase(server)
            admin_data = self.client.admins.auth_with_password("gcgbarbosa@gmail.com", ",ofX2(0/5t*P")
            token = admin_data.token

            # raise ValueError("Token or user & password must be provided")

    def check_auth(self) -> bool:
        if self.client.auth_store.model:
            return True

        return False

    def create_chatbot_interaction(self, user_name: str, session_id: str, interaction_settings_id: str) -> ChatbotInteractionRecord:
        result = self.client.collection("chatbot_interactions").create(
            {
                "elapsed_time": 0,
                "user_name": user_name,
                "session_id": session_id,
                "interaction_settings_id": interaction_settings_id,
                "is_finished": False,
            }
        )

        return ChatbotInteractionRecord(
            id=result.id,
            elapsed_time=result.elapsed_time,  # type: ignore
            created=result.created,  # type: ignore
            updated=result.updated,  # type: ignore
            is_finished=result.is_finished,  # type: ignore
            user_name=result.user_name,  # type: ignore
            session_id=result.session_id,  # type: ignore
            interaction_settings_id=result.interaction_settings_id,  # type: ignore
        )

    def create_interaction_settings(
        self, name: str, system_prompt: str, chatbot_settings: list[dict[str, str]]
    ) -> InteractionSettingsRecord:
        # Create the interaction settings first
        #

        all_chatbots = [c.id for c in self.list_chatbots()]
        provided_chatbot_ids = [s.get("chatbot_id") for s in chatbot_settings]

        if len(all_chatbots) != len(provided_chatbot_ids):
            raise ValueError("There should be provided one chatbot per")

        missing_chatbots = [cid for cid in all_chatbots if cid not in provided_chatbot_ids]

        if missing_chatbots:
            raise ValueError(f"Missing settings for chatbots: {missing_chatbots}")

        result = self.client.collection("interaction_settings").create(
            {
                "name": name,
                "system_prompt": system_prompt,
            }
        )

        inserted_settings = []

        for setting in chatbot_settings:
            chatbot_id = setting.get("chatbot_id")
            system_message = setting.get("system_message")

            if chatbot_id is None or system_message is None:
                self.client.collection("interaction_settings").delete(result.id)
                for inserted_id in inserted_settings:
                    self.client.collection("chatbot_settings").delete(inserted_id)

                raise ValueError("Each chatbot setting must have 'chatbot_id' and 'system_message'")

            inserted = self.client.collection("chatbot_settings").create(
                {
                    "chatbot_id": chatbot_id,
                    "system_message": system_message,
                    "interaction_settings_id": result.id,
                }
            )

            inserted_settings.append(inserted.id)

        return InteractionSettingsRecord(
            id=result.id,
            name=result.name,  # type: ignore
            system_prompt=result.system_prompt,  # type: ignore
            created=result.created,  # type: ignore
            updated=result.updated,  # type: ignore
        )

    @overload
    def update_chatbot_interaction(self, interaction_id: str, *, is_finished: bool) -> ChatbotInteractionRecord: ...
    @overload
    def update_chatbot_interaction(self, interaction_id: str, *, elapsed_time: int) -> ChatbotInteractionRecord: ...
    @overload
    def update_chatbot_interaction(
        self, interaction_id: str, *, interaction_settings_id: str
    ) -> ChatbotInteractionRecord: ...

    def update_chatbot_interaction(
        self,
        interaction_id: str,
        is_finished: bool | None = None,
        elapsed_time: int | None = None,
        interaction_settings_id: str | None = None,
    ) -> ChatbotInteractionRecord:
        params: dict = {}
        if is_finished is not None:
            params["is_finished"] = is_finished
        if elapsed_time is not None:
            params["elapsed_time"] = elapsed_time
        if interaction_settings_id is not None:
            params["interaction_settings_id"] = interaction_settings_id

        interaction_record = self.client.collection("chatbot_interactions").update(
            id=interaction_id, body_params=params
        )

        record_result = ChatbotInteractionRecord(
            id=interaction_record.id,
            elapsed_time=interaction_record.elapsed_time,  # type: ignore
            created=interaction_record.created,  # type: ignore
            updated=interaction_record.updated,  # type: ignore
            is_finished=interaction_record.is_finished,  # type: ignore
            user_name=interaction_record.user_name,  # type: ignore
            session_id=interaction_record.session_id,  # type: ignore
            interaction_settings_id=interaction_record.interaction_settings_id,  # type: ignore
        )

        return record_result

    def insert_message(
        self, role: str, content: str, interaction_id: str, chatbot_id: str | None = None
    ) -> MessageRecord:
        result = self.client.collection("messages").create(
            {
                "role": role,
                "content": content,
                "interaction_id": interaction_id,
                "chatbot_id": chatbot_id,
            }
        )

        return MessageRecord(
            id=result.id,
            timestamp=result.timestamp,  # type: ignore
            role=result.role,  # type: ignore
            content=result.content,  # type: ignore
            interaction_id=result.interaction_id,  # type: ignore
            chatbot_id=result.chatbot_id,  # type: ignore
        )

    def get_chatbot_interaction(self, chatbot_interaction_id: str) -> ChatbotInteractionRecord:
        interaction_record = self.client.collection("chatbot_interactions").get_one(chatbot_interaction_id)

        record_result = ChatbotInteractionRecord(
            id=interaction_record.id,
            created=interaction_record.created,  # type: ignore
            updated=interaction_record.updated,  # type: ignore
            is_finished=interaction_record.is_finished,  # type: ignore
            elapsed_time=interaction_record.elapsed_time,  # type: ignore
            user_name=interaction_record.user_name,  # type: ignore
            session_id=interaction_record.session_id,  # type: ignore
            interaction_settings_id=interaction_record.interaction_settings_id,  # type: ignore
        )

        return record_result

    def list_chatbot_interactions_by_session(self, session_id: str) -> list[ChatbotInteractionRecord]:
        interaction_records = self.client.collection("chatbot_interactions").get_full_list(
            query_params={"filter": f'session_id = "{session_id}"'}
        )

        interaction_records = []
        for interaction_record in interaction_records:
            interaction_record = ChatbotInteractionRecord(
                id=interaction_record.id,
                elapsed_time=interaction_record.elapsed_time,  # type: ignore
                created=interaction_record.created,  # type: ignore
                updated=interaction_record.updated,  # type: ignore
                is_finished=interaction_record.is_finished,  # type: ignore
                user_name=interaction_record.user_name,  # type: ignore
                session_id=interaction_record.session_id,  # type: ignore
                interaction_settings_id=interaction_record.interaction_settings_id,  # type: ignore
            )
            interaction_records.append(interaction_record)

        return interaction_records

    def list_chatbots(self) -> list[ChatbotRecord]:
        chatbots = self.client.collection("chatbots").get_full_list()

        chatbot_records = []
        for chatbot in chatbots:
            chatbot_record = ChatbotRecord(
                id=chatbot.id,
                name=chatbot.name,  # type: ignore
                created=chatbot.created,  # type: ignore
                updated=chatbot.updated,  # type: ignore
            )

            chatbot_records.append(chatbot_record)

        return chatbot_records

    def get_chatbot_settings(self, interaction_settings_id: str) -> list[ChatbotSettingsRecord]:
        try:
            settings_records = self.client.collection("interaction_settings").get_one(
                interaction_settings_id,
                query_params={"expand": "chatbot_settings_via_interaction_settings_id"},
            )

            records_result = []
            chatbot_settings = settings_records.expand.get("chatbot_settings_via_interaction_settings_id")

            if chatbot_settings is None:
                return []

            for s in chatbot_settings:
                r = ChatbotSettingsRecord(
                    id=s.id,
                    system_message=s.system_message,  # type: ignore
                    chatbot_id=s.chatbot_id,  # type: ignore
                    interaction_settings_id=s.interaction_settings_id,  # type: ignore
                    created=s.created,  # type: ignore
                    updated=s.updated,  # type: ignore
                )

                records_result.append(r)

            return records_result

        except Exception as e:
            logger.error(f"Error fetching chatbot settings: {e}")
            return []

    def get_interaction_setting(self, interaction_settings_id: str) -> InteractionSettingsRecord | None:
        try:
            setting_record = self.client.collection("interaction_settings").get_one(
                interaction_settings_id,
            )

            record_result = InteractionSettingsRecord(
                id=setting_record.id,
                name=setting_record.name,  # type: ignore
                system_prompt=setting_record.system_prompt,  # type: ignore
                created=setting_record.created,  # type: ignore
                updated=setting_record.updated,  # type: ignore
            )

            return record_result

        except Exception as e:
            logger.error(f"Error fetching chatbot settings: {e}")
            return None

    def list_interaction_settings(self) -> list[InteractionSettingsRecord]:
        try:
            setting_records = self.client.collection("interaction_settings").get_full_list()

            result_records = []
            for setting_record in setting_records:
                record_result = InteractionSettingsRecord(
                    id=setting_record.id,
                    name=setting_record.name,  # type: ignore
                    system_prompt=setting_record.system_prompt,  # type: ignore
                    created=setting_record.created,  # type: ignore
                    updated=setting_record.updated,  # type: ignore
                )

                result_records.append(record_result)

            return result_records

        except Exception as e:
            logger.error(f"Error listing interaction settings: {e}")
            return []

    def list_messages_by_interaction(self, interaction_id: str) -> list[MessageRecord]:
        try:
            interaction_record = self.client.collection("chatbot_interactions").get_one(
                interaction_id,
                query_params={"expand": "messages_via_interaction_id"},
            )

            records_result = []
            messages = interaction_record.expand.get("messages_via_interaction_id")

            if messages is None:
                return []

            for message in messages:
                message_record = MessageRecord(
                    id=message.id,
                    role=message.role,  # type: ignore
                    content=message.content,  # type: ignore
                    interaction_id=message.interaction_id,  # type: ignore
                    chatbot_id=message.chatbot_id,  # type: ignore
                    timestamp=message.timestamp,  # type: ignore
                )

                records_result.append(message_record)

            return records_result

        except Exception as e:
            logger.error(f"Error fetching messages for interaction {interaction_id}: {e}")
            return []

    def create_feedback(self, interaction_id: str, feedback_string: str) -> FeedbackRecord:
        result = self.client.collection("feedbacks").create(
            {
                "feedback": feedback_string,
                "interaction_id": interaction_id,
            }
        )

        return FeedbackRecord(
            id=result.id,
            interaction_id=result.interaction_id,  # type: ignore
            feedback=result.feedback,  # type: ignore
            created=result.created,  # type: ignore
            updated=result.updated,  # type: ignore
        )


if __name__ == "__main__":
    # Create an instance of AuthManager
    db = PocketBaseDB()

    chatbots = db.list_chatbots()
    # print(chatbots)

    # interaction = db.create_chatbot_interaction("test_user", "session_123")
    # print(interaction)

    db.update_chatbot_interaction("ttvxe4qk4erlw4a", is_finished=True)
    db.update_chatbot_interaction("ttvxe4qk4erlw4a", elapsed_time=150)

    interaction = db.get_chatbot_interaction("ttvxe4qk4erlw4a")
    # print(interaction)

    interactions = db.list_chatbot_interactions_by_session("session_123")
    # print(interactions)

    settings = db.get_interaction_setting("default00000000")
    # print(settings)

    settings = db.get_chatbot_settings("default00000000")
    # print(settings)

    settings = db.list_interaction_settings()
    # print(settings)

    # settings = db.create_interaction_settings(
    #     name="Test Interaction Settings",
    #     system_prompt="This is a test system prompt.",
    #     chatbot_settings=[
    #         {"chatbot_id": "chatbot00000001", "system_message": "System message for chatbot 1"},
    #         {"chatbot_id": "chatbot00000002", "system_message": "System message for chatbot 2"},
    #         {"chatbot_id": "chatbot00000003", "system_message": "System message for chatbot 2"},
    #     ],
    # )
    # print(settings)

    # message = db.insert_message(
    #     role="system", content="Hello", interaction_id="ttvxe4qk4erlw4a", chatbot_id="chatbot00000001"
    # )
    # print(message)

    messages = db.list_messages_by_interaction("ttvxe4qk4erlw4a")
    # print(messages)

    feedback = db.create_feedback("ttvxe4qk4erlw4a", '{"hello": "world"}')

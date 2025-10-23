import os

from pocketbase import PocketBase
from pocketbase.stores.base_auth_store import BaseAuthStore

from src.models import ChatbotRecord, ChatbotInteractionRecord, MessageRecord

from typing import overload


class PocketBaseDB:
    def __init__(self, token: str | None = None, email: str | None = None, password: str | None = None):
        server = os.getenv("POCKETBASE_URL")

        if not server:
            raise ValueError("POCKETBASE_URL environment variable is not set")

        # self.client = PocketBase(server)
        admin_data = self.client.admins.auth_with_password("gcgbarbosa@gmail.com", ",ofX2(0/5t*P")
        token = admin_data.token

        if email and password:
            self.client = PocketBase(server)
            self.client.collection("users").auth_with_password(email, password)

        elif token:
            auth = BaseAuthStore(base_token=token)
            self.client = PocketBase(server, auth_store=auth)
        else:
            raise ValueError("Token or user & password must be provided")

    def check_auth(self) -> bool:
        if self.client.auth_store.model:
            return True

        return False

    def create_chatbot_interaction(self, user_id: str, chatbot_id: str, position: int) -> ChatbotInteractionRecord:
        result = self.client.collection("chatbot_interactions").create(
            {
                "elapsed_time": 0,
                "position": position,
                "chatbot_id": chatbot_id,
                "user_id": user_id,
                "is_finished": False,
            }
        )

        return ChatbotInteractionRecord(
            id=result.id,
            elapsed_time=result.elapsed_time,  # type: ignore
            position=result.position,  # type: ignore
            created=result.created,  # type: ignore
            updated=result.updated,  # type: ignore
            is_finished=result.is_finished,  # type: ignore
            chatbot_id=result.chatbot_id,  # type: ignore
            user_id=result.user_id,  # type: ignore
        )

    @overload
    def update_interaction(self, interaction_id: str, *, is_finished: bool) -> ChatbotInteractionRecord: ...
    @overload
    def update_interaction(self, interaction_id: str, *, elapsed_time: int) -> ChatbotInteractionRecord: ...

    def update_interaction(
        self,
        interaction_id: str,
        is_finished: bool | None = None,
        elapsed_time: int | None = None,
    ) -> ChatbotInteractionRecord:
        params: dict = {}
        if is_finished is not None:
            params["is_finished"] = is_finished
        if elapsed_time is not None:
            params["elapsed_time"] = elapsed_time

        interaction = self.client.collection("chatbot_interactions").update(id=interaction_id, body_params=params)

        interaction_record = ChatbotInteractionRecord(
            id=interaction.id,
            elapsed_time=interaction.elapsed_time,  # type: ignore
            position=interaction.position,  # type: ignore
            created=interaction.created,  # type: ignore
            updated=interaction.updated,  # type: ignore
            user_id=interaction.user_id,  # type: ignore
            is_finished=interaction.is_finished,  # type: ignore
            chatbot_id=interaction.chatbot_id,  # type: ignore
        )

        return interaction_record

    def insert_message(self, role: str, content: str, interaction_id: str) -> MessageRecord:
        result = self.client.collection("messages").create(
            {
                "role": role,
                "content": content,
                "interaction_id": interaction_id,
            }
        )

        return MessageRecord(
            id=result.id,
            timestamp=result.timestamp,  # type: ignore
            role=result.role,  # type: ignore
            content=result.content,  # type: ignore
            interaction_id=result.interaction_id,  # type: ignore
        )

    def get_chatbot_interaction(self, chatbot_interaction_id: str) -> ChatbotInteractionRecord:
        interaction = self.client.collection("chatbot_interactions").get_one(
            id=chatbot_interaction_id,
            query_params={"expand": "messages_via_interaction_id, chatbot_id"},
        )

        message_records = []
        for message in interaction.expand.get("messages_via_interaction_id", []):
            message_record = MessageRecord(
                id=message.id,
                role=message.role,
                content=message.content,
                interaction_id=interaction.id,
                timestamp=message.timestamp,
            )
            message_records.append(message_record)

        chatbot = interaction.expand.get("chatbot_id", None)
        chatbot_record = None
        if chatbot is not None:
            chatbot_record = ChatbotRecord(
                id=chatbot.id,  # type.ignore
                name=chatbot.name,  # type: ignore
                created=chatbot.created,  # type: ignore
                updated=chatbot.updated,  # type: ignore
            )

        interaction_record = ChatbotInteractionRecord(
            id=interaction.id,
            elapsed_time=interaction.elapsed_time,  # type: ignore
            position=interaction.position,  # type: ignore
            created=interaction.created,  # type: ignore
            updated=interaction.updated,  # type: ignore
            user_id=interaction.user_id,  # type: ignore
            is_finished=interaction.is_finished,  # type: ignore
            chatbot_id=interaction.chatbot_id,  # type: ignore
            messages=message_records,
            chatbot=chatbot_record,
        )

        return interaction_record

    def list_chatbot_interactions(self, user_id: str) -> list[ChatbotInteractionRecord]:
        user_data = self.client.collection("chatbot_interactions").get_full_list(
            query_params={"filter": f'user_id = "{user_id}"'}
        )

        interaction_records = []

        for interaction in user_data:
            interaction = ChatbotInteractionRecord(
                id=interaction.id,
                elapsed_time=interaction.elapsed_time,  # type: ignore
                position=interaction.position,  # type: ignore
                created=interaction.created,  # type: ignore
                updated=interaction.updated,  # type: ignore
                user_id=interaction.user_id,  # type: ignore
                chatbot_id=interaction.chatbot_id,  # type: ignore
                is_finished=interaction.is_finished,  # type: ignore
            )

            interaction_records.append(interaction)

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


if __name__ == "__main__":
    # Create an instance of AuthManager
    db = PocketBaseDB()

    # interactions = db.list_chatbot_interactions("flyj221r8b3rfdf")
    # print(interactions)

    # chatbots = db.list_chatbots()
    # print(chatbots)

    # interaction = db.create_chatbot_interaction("flyj221r8b3rfdf", "t4k57b5z9gxhaba", 2)
    # print(interaction)

    interaction = db.get_chatbot_interaction("w986dg1gjzxqbw4")
    print(interaction)

    # message = db.insert_message("system", content="Hello", interaction_id="w986dg1gjzxqbw4")
    # print(message)

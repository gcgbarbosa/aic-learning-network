from nicegui import ui
from nicegui.elements.button import Button
from nicegui.elements.grid import Grid
from nicegui.elements.textarea import Textarea

from src.flow_manager import FlowManager

from .messages_container import MessagesContainerComponent

from loguru import logger

import asyncio


class ChatbotsContainerComponent:
    def __init__(self, flow_manager: FlowManager):
        with ui.grid(columns=3).classes("w-full absolute-full px-4 pt-4") as container:
            chatbot_id, chatbot, messages = flow_manager.get_chatbot_01()
            m1 = MessagesContainerComponent(
                "Chatbot #1",
                chatbot,
                messages,
                lambda e, chatbot_id=chatbot_id: flow_manager.save_assistant_message(content=e, chatbot_id=chatbot_id),
            )
            logger.info(f"Initialized Chatbot 1 with ID: {chatbot_id}")

            chatbot_id, chatbot, messages = flow_manager.get_chatbot_02()
            m2 = MessagesContainerComponent(
                "Chatbot #2",
                chatbot,
                messages,
                lambda e, chatbot_id=chatbot_id: flow_manager.save_assistant_message(content=e, chatbot_id=chatbot_id),
            )
            logger.info(f"Initialized Chatbot 2 with ID: {chatbot_id}")

            chatbot_id, chatbot, messages = flow_manager.get_chatbot_03()
            m3 = MessagesContainerComponent(
                "Chatbot #3",
                chatbot,
                messages,
                lambda e, chatbot_id=chatbot_id: flow_manager.save_assistant_message(content=e, chatbot_id=chatbot_id),
            )
            logger.info(f"Initialized Chatbot 3 with ID: {chatbot_id}")

        self._chatbot_container = container

        self._message_containers = {1: m1, 2: m2, 3: m3}

        self._flow_manager = flow_manager

    @property
    def element(self) -> Grid:
        return self._chatbot_container

    def freeze(self) -> None:
        self._chatbot_container.classes.remove("absolute-full")
        self._chatbot_container.classes.append("h-120")

    def get_message_container(self, index):
        if index < 1 or index > len(self._message_containers):
            raise ValueError("Index out of range")

        return self._message_containers.get(index)

    async def process_user_prompt(self, txt_input_chat: Textarea, btn_input_chat: Button) -> None:
        user_prompt = txt_input_chat.value

        self._flow_manager.save_user_message(user_prompt)

        txt_input_chat.value = ""
        txt_input_chat.disable()
        btn_input_chat.disable()

        tasks = [container.add_message(user_prompt) for container in self._message_containers.values()]

        await asyncio.gather(*tasks)

        txt_input_chat.enable()
        btn_input_chat.enable()

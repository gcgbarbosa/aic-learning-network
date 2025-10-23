from nicegui import ui
from nicegui.elements.button import Button
from nicegui.elements.grid import Grid
from nicegui.elements.textarea import Textarea

from .messages_container import MessagesContainerComponent

from loguru import logger

import asyncio


class ChatbotsContainerComponent:
    def __init__(self):
        with ui.grid(columns=3).classes("w-full absolute-full px-4 pt-4") as container:
            m1 = MessagesContainerComponent()
            # ui.space()
            m2 = MessagesContainerComponent()
            # ui.space()
            m3 = MessagesContainerComponent()

        self._chatbot_container = container

        self._message_containers = {1: m1, 2: m2, 3: m3}

    @property
    def element(self) -> Grid:
        return self._chatbot_container

    def get_message_container(self, index):
        if index < 1 or index > len(self._message_containers):
            raise ValueError("Index out of range")

        return self._message_containers.get(index)

    async def process_user_prompt(self, txt_input_chat: Textarea, btn_input_chat: Button) -> None:
        # TODO: add message from user to DB
        user_prompt = txt_input_chat.value

        txt_input_chat.value = ""
        txt_input_chat.disable()
        btn_input_chat.disable()


        # Launch all container calls at once
        tasks = [container.add_message(user_prompt) for index, container in self._message_containers.items()]

        await asyncio.gather(*tasks)

        txt_input_chat.enable()
        btn_input_chat.enable()

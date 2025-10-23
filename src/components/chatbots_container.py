from nicegui import ui
from nicegui.elements.grid import Grid

from .messages_container import MessagesContainerComponent


class ChatbotsContainerComponent:
    def __init__(self):
        with ui.grid(columns=3).classes("w-full absolute-full border px-4") as container:
            m1 = MessagesContainerComponent()
            # ui.space()
            m2 = MessagesContainerComponent()
            # ui.space()
            m3 = MessagesContainerComponent()

        self._chatbot_container = container

        self._message_container = {"1": m1, "2": m2, "3": m3}

    @property
    def element(self) -> Grid:
        return self._chatbot_container

    def get_message_container(self, index):
        if index < 1 or index > len(self._message_container):
            raise ValueError("Index out of range")

        return self._message_container.get(index)

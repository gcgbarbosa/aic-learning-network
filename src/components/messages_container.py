import random
from datetime import datetime, timezone

from nicegui import ui

from src.models import MessageRecord

time = datetime.now(tz=timezone.utc)


class MessagesContainerComponent:
    messages = [
        MessageRecord(id="test", timestamp=time, interaction_id="", role="user", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="assistant", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="user", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="assistant", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="user", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="assistant", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="user", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="assistant", content="Hello, how are you?"),
        MessageRecord(id="test", timestamp=time, interaction_id="", role="user", content="Hello, how are you?"),
    ]

    def __init__(self):
        n = random.randint(5, 10)  # random integer from 1 to 10
        messages = self.messages[:n]

        with ui.scroll_area().classes("h-full border") as scroll_area:
            with ui.element("div").classes("w-full"):
                ui.chat_message(
                    "Hello, I am here to assist you!", name="Assistant", avatar="https://robohash.org/robot"
                )

                for message in messages:
                    if message.role == "user":
                        ui.chat_message(message.content, name="You", avatar="https://robohash.org/person").props("sent")
                    elif message.role == "assistant":
                        ui.chat_message(message.content, name="Assistant", avatar="https://robohash.org/robot")

        scroll_area.scroll_to(percent=100)
        #         ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")
        #
        #         self._container = messages_container
        #

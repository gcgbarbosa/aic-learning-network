from datetime import datetime, timezone

from html_sanitizer import Sanitizer
from loguru import logger
from nicegui import ui

from src.chatbots import BaseChabot
from src.models import MessageRecord

time = datetime.now(tz=timezone.utc)


USER_AVATAR = "https://robohash.org/person"
ASSISTANT_AVATAR = "https://robohash.org/robot"


class MessagesContainerComponent:
    def __init__(self, chatbot_name: str, agent: BaseChabot, messages: list[MessageRecord], fn):
        with ui.scroll_area().classes("h-full border border-gray-300 rounded-sm") as scroll_area:
            with ui.element("div").classes("w-full pr-4") as message_container:
                # hello, I am here to assist you
                ui.chat_message("Hallo, hoe kan ik je helpen?", name=chatbot_name, avatar=ASSISTANT_AVATAR)

                for message in messages:
                    if message.role == "user":
                        with ui.chat_message(name="You", avatar=USER_AVATAR).props("sent"):
                            ui.markdown(message.content)
                    elif message.role == "assistant":
                        with ui.chat_message(name=chatbot_name, avatar=ASSISTANT_AVATAR):
                            ui.markdown(message.content)

        scroll_area.scroll_to(percent=100)

        self._chatbot_name = chatbot_name

        self._message_container = message_container
        self._scroll_area = scroll_area
        self._agent = agent

        self._fn = fn

    async def add_message(self, user_prompt: str):
        name = "U"

        with self._message_container:
            spinner = ui.spinner(size="lg")

        try:
            with self._message_container:
                ui.chat_message(user_prompt, name=name, avatar=USER_AVATAR).props("sent")
                self._scroll_area.scroll_to(percent=100)

                assistant_response = ui.chat_message(
                    name=self._chatbot_name,
                    avatar=ASSISTANT_AVATAR,
                    text_html=True,
                    sanitize=Sanitizer().sanitize,
                )

                assistant_response.set_visibility(False)
                first = True  # flag to track first streamed token

                with assistant_response:
                    content = ui.markdown("")

                    async for m in self._agent.stream_response(user_prompt):
                        if first:
                            self._message_container.remove(spinner)
                            assistant_response.set_visibility(True)  # show only on first token
                            first = False

                        content.set_content(m)

                        self._scroll_area.scroll_to(percent=100)

                    logger.info(f"Message added to interaction: q:[{user_prompt}] -> a:[{content.content}]")

                self._fn(content.content)

        except Exception as e:
            ui.notify(f"Error trying to generate a response: {e}")
            logger.error(f"Error trying to generate a response: {e}")
            return None

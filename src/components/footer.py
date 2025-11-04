from loguru import logger
from nicegui import ui
from nicegui.elements.footer import Footer
from nicegui.events import GenericEventArguments

from src.components.chatbots_container import ChatbotsContainerComponent


class FooterComponent:
    def __init__(self, chatbot_container: ChatbotsContainerComponent):
        with ui.footer().classes("bg-white") as footer:
            with ui.row().classes("items-center w-full max-w-3xl mx-auto  shadow-xl p-1 rounded-md"):
                text = (
                    ui.textarea(placeholder="Ask anything")
                    .props("outlined rows=4 maxlength=4000")
                    .classes("col-grow height-full")
                )

                button = ui.button(icon="send").props("push id='btn_send'")
                button.on("click", self.send_user_prompt)
                button.disable()

                text.on(
                    "keydown",
                    lambda e: self.handle_key_down(e),
                )
                text.disable()

                self._txt_input_chat = text
                self._btn_input_chat = button

        self._element = footer

        self._chatbot_container = chatbot_container

        # self.prevent_new_line_on_enter()

    def enable_chat(self) -> None:
        self._btn_input_chat.enable()
        self._txt_input_chat.enable()

    def disable_chat(self) -> None:
        self._btn_input_chat.disable()
        self._txt_input_chat.disable()

    def hide(self) -> None:
        self._element.visible = False

    async def send_user_prompt(self):
        await self._chatbot_container.process_user_prompt(self._txt_input_chat, self._btn_input_chat)

    async def handle_key_down(
        self,
        e: GenericEventArguments,
    ):
        if e.args.get("shiftKey") and e.args.get("key") == "Enter":
            logger.info("User pressed shift+enter")
        elif e.args.get("key") == "Enter":
            await self.send_user_prompt()

    def prevent_new_line_on_enter(self):
        ui.run_javascript("""
            document.addEventListener("keydown", function (event) {
                if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();  // stop newlines or form submissions
                }
            });
        """)

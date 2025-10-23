from loguru import logger
from nicegui import ui
from nicegui.elements.footer import Footer
from nicegui.events import GenericEventArguments


class FooterComponent:
    def __init__(
        self,
    ):
        with ui.footer().classes("bg-white") as footer:
            with ui.row().classes("items-center w-full max-w-3xl mx-auto p-2 shadow-xl"):
                text = ui.textarea(placeholder="Ask anything").props("outlined rows=4").classes("col-grow height-full")

                button = ui.button(icon="send").props("push id='btn_send'")
                button.on("click", lambda: ui.notify("Button clicked"))
                button.disable()

                text.on(
                    "keydown",
                    lambda e: self.handle_key_down(e),
                )
                text.disable()

                self.txt_input_chat = text
                self.btn_input_chat = button

        self._element = footer

    @property
    def element(self) -> Footer:
        return self._element

    async def handle_key_down(
        self,
        e: GenericEventArguments,
    ):
        if e.args.get("shiftKey") and e.args.get("key") == "Enter":
            logger.info("User pressed shift+enter")
        elif e.args.get("key") == "Enter":
            ui.notify("Enter pressed")
            # await self.message_controller.add_message(self.txt_input_chat, self.btn_input_chat)

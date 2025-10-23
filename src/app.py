"""Entrypoint"""

from loguru import logger
from nicegui import ui

from components import ChatbotsContainerComponent, FooterComponent, HeaderComponent

from src.controllers import TimerModel

logger.info("Initializing AI-Cares application")


@ui.page("/")
def main():
    """
    Main function that prints a greeting message and returns the sum of 1 and 1.

    This function outputs a simple greeting to the console and computes a basic arithmetic
    operation.

    Returns:
        int: The result of the arithmetic operation (1 + 1), which is 2.
    """

    TIME_PER_STEP = 5
    elapsed_time = 0
    timer_model = TimerModel(max(0, TIME_PER_STEP - elapsed_time))

    timer = ui.timer(1.0, callback=lambda: ui.notify("The application is not ready yet"), active=False)

    ui.page_title("AI-Cares")

    HeaderComponent(timer_model, timer)

    chat_container = ChatbotsContainerComponent()

    # chat_container.get_message_container(3)

    footer = FooterComponent(chat_container)

    footer._btn_input_chat.enable()
    footer._txt_input_chat.enable()

    def countdown():
        has_time_left = timer_model.remaining > 0

        if has_time_left:
            timer_model.remaining -= 1
            return

        timer.active = False

        footer.element.hide()

        chat_container.element.classes.remove("absolute-full")
        chat_container.element.classes.append("h-150")

        ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")

    timer.callback = countdown

    # timer.active = True


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        storage_secret="THIS_NEEDS_TO_BE_CHANGED",
        port=8880,
        favicon="https://thomasmore.be/themes/custom/tm/assets/images/favicon/favicon.ico",
    )

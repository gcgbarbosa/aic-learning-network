"""Entrypoint"""

from loguru import logger
from nicegui import ui

from components import (
    ChatbotsContainerComponent,
    FooterComponent,
    HeaderComponent,
    SettingsModalComponent,
    FeedbackComponent,
)

from src.components.session_modal import SessionModalComponent
from src.controllers import TimerModel
from src.flow_manager import FlowManager

logger.info("Initializing AI-Cares application")


@ui.page("/")
def main():
    ui.colors(secondary="#f58732", primary="#009ad4", accent="#5ab031")

    flow_manager = FlowManager()

    # SessionModalComponent(flow_manager)

    TIME_PER_STEP = 5
    elapsed_time = 0
    timer_model = TimerModel(max(0, TIME_PER_STEP - elapsed_time))

    timer = ui.timer(1.0, callback=lambda: ui.notify("The application is not ready yet"), active=False)

    ui.page_title("AI-Cares")

    settings_component = SettingsModalComponent(flow_manager)
    # settings_component.show()

    HeaderComponent(timer_model, timer, settings_component)

    chat_container = ChatbotsContainerComponent(flow_manager)

    footer = FooterComponent(chat_container)

    # TODO: remove after test
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
    chat_container.element.classes.append("h-120")

    FeedbackComponent()

    ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")

    timer.callback = countdown

    # footer.element.hide()
    # chat_container.element.classes.remove("absolute-full")
    # chat_container.element.classes.append("h-150")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        storage_secret="THIS_NEEDS_TO_BE_CHANGED",
        port=8880,
        favicon="https://thomasmore.be/themes/custom/tm/assets/images/favicon/favicon.ico",
    )

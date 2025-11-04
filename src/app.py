"""Entrypoint"""

from loguru import logger
from nicegui import ui

from components import (
    ChatbotsContainerComponent,
    FeedbackComponent,
    FooterComponent,
    HeaderComponent,
    SettingsModalComponent,
)
from src.components.session_modal import SessionModalComponent
from src.controllers import TimerModel
from src.flow_manager import FlowManager
import os

logger.info("Initializing AI-Cares application")


@ui.page("/")
def main():
    ui.colors(secondary="#f58732", primary="#009ad4", accent="#5ab031")

    # TODO: remove this
    # interaction_id = app.storage.user.get("interaction_id", None)
    # ui.notify(interaction_id)
    # app.storage.user["interaction_id"] = "ttvxe4qk4erlw4a"

    flow_manager = FlowManager()

    settings_component = None
    if flow_manager.interaction_id is None:
        SessionModalComponent(flow_manager)
        settings_component = SettingsModalComponent(flow_manager)

    TIME_PER_STEP = int(os.getenv("TIME_PER_STEP", 120))
    elapsed_time = flow_manager.get_elapsed_time()

    timer_model = TimerModel(max(0, TIME_PER_STEP - elapsed_time))

    timer = ui.timer(1.0, callback=lambda: ui.notify("The application is not ready yet"), active=False)

    ui.page_title("AI-Cares")

    chat_container = ChatbotsContainerComponent(flow_manager)

    footer = FooterComponent(chat_container)

    HeaderComponent(timer_model=timer_model, timer=timer, settings_component=settings_component, footer=footer)

    feedback = FeedbackComponent(flow_manager)

    def countdown():
        has_time_left = timer_model.remaining > 0

        if has_time_left:
            if timer_model.remaining % 10 == 0:
                flow_manager.updated_elapsed_time(TIME_PER_STEP - timer_model.remaining)

            timer_model.remaining -= 1
            return

        timer.active = False
        flow_manager.updated_elapsed_time(TIME_PER_STEP)

        footer.hide()
        chat_container.freeze()

        feedback.show()

    if elapsed_time >= TIME_PER_STEP:
        timer.activate()

    ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")

    timer.callback = countdown


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        storage_secret="THIS_NEEDS_TO_BE_CHANGED",
        port=8880,
        favicon="https://thomasmore.be/themes/custom/tm/assets/images/favicon/favicon.ico",
    )

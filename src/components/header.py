from nicegui import ui

from datetime import timedelta

from nicegui.timer import Timer

from src.components.settings_modal import SettingsModalComponent
from src.controllers.timer import TimerModel


class HeaderComponent:
    def __init__(self, timer_model: TimerModel, timer: Timer, settings_component: SettingsModalComponent):
        # name = app.storage.user.get("name", "User")
        
        self._timer = timer

        with ui.header().classes("items-center"):
            ui.label().bind_text_from(timer_model, "remaining", backward=self.format_time_left).classes(
                "text-lg font-bold"
            )

            self._start_btn = ui.button(text="Start conversation", on_click=self.toggle_timer).props(
                "outline color=white"
            )
            self._start_btn.bind_visibility_from(timer_model, "remaining", backward=lambda v: v > 0)

            self._config_btn = (
                ui.button(icon="settings", on_click=lambda: settings_component.show())
                .classes("outlined")
                .props("outline color=white ")
            )

            ui.space()

            ui.button(
                text="End conversation",
                on_click=lambda: self.handle_end_conversation(timer_model=timer_model),
                icon="close",
            ).props("outline color=white").bind_visibility_from(timer_model, "remaining", backward=lambda v: v > 0)

    def handle_end_conversation(self, timer_model: TimerModel):
        if not self._timer.active:
            self.toggle_timer()

        timer_model.set_remaining_time(0)

    def toggle_timer(self):
        if self._timer.active:
            self._timer.deactivate()
            self._start_btn.set_text("Start conversation")

        else:
            self._timer.activate()
            self._config_btn.visible = False
            self._start_btn.set_text("Pause conversation")

    def format_time_left(self, seconds: int) -> str:
        """Format countdown seconds into mm:ss string (skip hours)."""
        return "Time left: " + str(timedelta(seconds=seconds))[2:]

from nicegui import ui

from src.flow_manager import FlowManager


class SessionModalComponent:
    def __init__(self, flow_manager: FlowManager):
        self._fm = flow_manager

        self.session_id: str | None = None
        self.user_name: str | None = None

        with ui.dialog().props("persistent") as dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                ui.input("Session ID", on_change=lambda e: setattr(self, "session_id", e.value)).classes("w-80")
                ui.input("Your name", on_change=lambda e: setattr(self, "user_name", e.value)).classes("w-80")

                # ui.select(
                #     options=names,
                #     # on_change=lambda e: setattr(self, "selected_theme", self.themes_dict[e.value]),
                # ).classes("w-40").props("label='Select theme'")

                ui.button("Confirm", on_click=self.handle_confirm).props("color=secondary").classes("w-full")

        dialog.open()
        self.dialog = dialog

    def handle_confirm(self) -> None:
        if not self.session_id or not self.user_name:
            ui.notify("Please enter both Session ID and Your name before confirming.", color="negative")
            return

        ui.notify(f"Session started for {self.user_name} with ID {self.session_id}", color="positive")

        self.dialog.close()

    #     """Confirm selection or ask the user to pick a theme."""
    #     if not self.selected_theme:
    #         ui.notify("Please select a theme before confirming.")
    #     else:
    #         # ui.notify(f"Theme ID: {self.selected_theme}")
    #
    #         self._fm.set_theme(self.selected_theme)
    #
    #         self._fm.start_interaction()
    #
    #         # self.im.add_message("user", "test")
    #
    #         # self.im.add_feedback(5, "Great!")
    #         # self.im.finish_interaction()
    #
    #         self.dialog.close()

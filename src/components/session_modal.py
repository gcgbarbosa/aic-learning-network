from nicegui import ui

from src.flow_manager import FlowManager


class SessionModalComponent:
    def __init__(self, flow_manager: FlowManager):
        self._fm = flow_manager

        self.session_id: str | None = None
        self.user_name: str | None = None

        with ui.dialog().props("persistent") as dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                ui.label("Pleace confirm that you accept the terms before proceeding")

                ui.button("Confirm", on_click=self.handle_confirm).props("color=secondary").classes("w-full")

        dialog.open()
        self.dialog = dialog

    def handle_confirm(self) -> None:
        ui.notify("New session started", color="info")

        self._fm.start_flow()

        self.dialog.close()


        # return

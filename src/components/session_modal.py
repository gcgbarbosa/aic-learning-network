from nicegui import ui

from src.flow_manager import FlowManager


class SessionModalComponent:
    def __init__(self, flow_manager: FlowManager):
        self._fm = flow_manager

        self.session_id: str | None = None
        self.user_name: str | None = None

        with ui.dialog().props("persistent") as dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                ui.label("Ik accepteerde de informed consent in de chat van de vergadering.")

                # confirm button
                ui.button("Bevestigen", on_click=self.handle_confirm).props("color=secondary").classes("w-full")

        dialog.open()
        self.dialog = dialog

    def handle_confirm(self) -> None:
        # new session started
        ui.notify("Nieuwe sessie gestart", color="info")

        self._fm.start_flow()

        self.dialog.close()

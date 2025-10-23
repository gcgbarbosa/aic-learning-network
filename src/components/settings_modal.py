from nicegui import ui


class SettingsModalComponent:
    def __init__(self):
        # self.general_prompt = ""

        with ui.dialog(value=True) as dialog:
            with ui.card().classes("w-5xl").style("max-width: none"):
                ui.textarea(
                    label="General Prompt",
                    placeholder="start typing",
                    on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                ).classes("w-full").props("outlined")
                general_prompt = ui.label("")

        # dialog.open()

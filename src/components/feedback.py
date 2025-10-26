from nicegui import ui
from nicegui.elements.row import Row


class FeedbackComponent:
    def __init__(self):
        with ui.row().classes("w-full") as row:
            with ui.column().classes("mx-4 p-8 w-full border border-gray-300 rounded-sm"):
                ui.label("Feedback Survey").classes("text-lg font-bold")

                self.result = {"comment": "", "rate": 1}

                ui.rating(
                    value=None,
                    size="lg",
                    icon="star",
                    icon_selected="star",
                ).bind_value_to(self.result, "rate")

                ui.textarea(placeholder="Do you have any comments?").props("outlined rows=4").classes(
                    "w-5xl"
                ).bind_value_to(self.result, "comment")

                ui.button("Submit feedback", on_click=lambda: ui.notify("hello"))

        self._row = row

    def element(self) -> Row:
        return self._row

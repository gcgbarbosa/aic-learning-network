from nicegui import ui


class MessagesComponent:
    def __init__(self):
        with ui.row().classes("w-full border"):
            ui.label("Left")
            ui.space()
            ui.label("Right")

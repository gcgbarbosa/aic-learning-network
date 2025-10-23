from nicegui import app, ui


class HeaderComponent:
    def __init__(self):
        # name = app.storage.user.get("name", "User")

        with ui.header().classes("items-center"):
            # with ui.row().classes("items-center w-full max-w-3xl mx-auto"):
            ui.label("AI-Cares")

            ui.space()
            # ui.label(f"{name}")
            # ui.icon("Testing interface")
            ui.button(text="Submit feedback", on_click=lambda: ui.notify("Feedback submited"), icon="feedback").props(
                "flat color=white"
            )

    # TODO: this must be moved to the footer
    def prevent_new_line_on_enter(self):
        ui.run_javascript("""
            document.addEventListener("keydown", function (event) {
                if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();  // stop newlines or form submissions
                }
            });
        """)

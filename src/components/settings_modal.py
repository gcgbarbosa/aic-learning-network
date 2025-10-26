from datetime import datetime

from nicegui import ui


class SettingsModalComponent:
    def __init__(self):

        general_prompt = ui.label("")
        with ui.dialog().classes("h-full") as dialog:
            with ui.card().classes("w-5xl h-full gap-2").style("max-width: none; hax-height: 90vh;"):
                with ui.card().classes("w-full").tight().props('flat bordered'):
                    with ui.card_section().classes("w-full p-2"):
                        with ui.row().classes("w-full items-center gap-2"):
                            ui.label("General system prompt").classes("text-xl")
                            ui.space()
                            ui.input("Settings name").props('outlined dense size="15px"').classes("w-64")
                            ui.button("Save settings", icon="settings").props('size="15px"')

                    with ui.element("div").classes("w-full"):
                        ui.textarea(
                            label="System prompt",
                            # placeholder="Write the system prompt",
                            on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                        ).classes("mx-2 mb-2").props("outlined input-class='h-full' input-style='resize: none'")


                self.files("1")
                self.files("2")
                self.files("3")

        self._dialog = dialog

    def show(self):
        self._dialog.open()

    def hide(self):
        self._dialog.close()

    def files(self, chatbot):
        with ui.card().classes("w-full").tight().props('flat bordered'):
            with ui.card_section().classes("w-full p-2"):
                with ui.row().classes("w-full items-center"):
                    ui.label(f"Chatbot #{chatbot}").classes("text-xl")
                    ui.space()
                    ui.button("Add files", icon="save").props("outline")

            with ui.grid(columns="3fr 1fr").classes("w-full h-full gap-0"):
                # with ui.scroll_area().classes("w-full h-full"):
                #     ui.codemirror("\n\n\n", language="Markdown").classes("h-full")
                with ui.element("div").classes("mx-2 mb-2"):
                    ui.textarea(
                        label="System prompt",
                        # placeholder="Write the system prompt",
                        # on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                    ).classes("w-full").props("outlined input-class='h-full' input-style='resize: none'")

                with ui.element("div").classes("mr-2 mb-2 rounded-sm border border-gray-300"):
                    with ui.scroll_area().classes("w-full h-full"):
                        document_list = ui.list().props("separator").classes("m-0 w-full")
                        with document_list:
                            for i in [1, 2, 3, 4, 5, 6]:
                                item = ui.item(
                                    # on_click=lambda d=doc, did=doc_id: toggle_file_selection(did, d.file_name, selected_items.get(did))  # type: ignore
                                    on_click=lambda: ui.notify("clicked")
                                ).classes("w-full")

                                with item:
                                    with ui.item_section().props("avatar"):
                                        ui.icon("picture_as_pdf").classes("text-red")

                                    with ui.item_section():
                                        ui.item_label("file.pdf")
                                        status = "test"
                                        total_chunks = 10
                                        upload_date = datetime.now()

                                        ui.item_label(f"{status} • {total_chunks} chunks").props("caption")
                                        # ui.item_label(
                                        #     f"Uploaded: {upload_date.strftime('%Y-%m-%d %H:%M')}"
                                        # ).props("caption")

            ui.query(".q-scrollarea__content").style("padding: 0px")

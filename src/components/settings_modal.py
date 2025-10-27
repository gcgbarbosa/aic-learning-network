from datetime import datetime

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from src.flow_manager import FlowManager
from src.models.interaction_setting import InteractionSettingsRecord

from loguru import logger


class SettingsModalComponent:
    def get_interaction_setting(self, interaction_id: str) -> InteractionSettingsRecord:
        default_settings = [setting for setting in self._settings_list if setting.id == interaction_id]
        if len(default_settings) != 1:
            raise ValueError("There should be exactly one default settings")
        default_setting = default_settings[-1]

        return default_setting

    def __init__(self, flow_manager: FlowManager):
        self._flow_manager = flow_manager

        interaction = self._flow_manager.get_interaction()

        self._system_prompt_text_area = {}

        chatbot_ids = self._flow_manager.get_chatbot_ids()

        # find the default setting
        self._settings_list = self._flow_manager.list_settings()
        settings_list_names = [s.name for s in self._settings_list]

        interaction_setting, chatbot_settings = self._flow_manager.get_interaction_and_chatbot_settings(
            interaction.interaction_settings_id
        )
        self._interaction_setting = (
            interaction_setting  # self.get_interaction_setting(interaction_id=interaction.interaction_settings_id)
        )
        self._chatbot_settings = chatbot_settings

        self._system_prompt_value = {idx: setting.system_message for idx, setting in self._chatbot_settings.items()}

        self._selected_interaction_setting = self._interaction_setting.name

        self._general_prompt = self._interaction_setting.system_prompt

        with ui.dialog().props("persistent") as naming_dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                name = ui.input(
                    "Setting name"  # , on_change=lambda e: setattr(self, "selected_interaction_setting", e.value)
                ).classes("w-80")

                ui.button("Confirm", on_click=lambda: ui.notify(name.value)).props(
                    "color=secondary",
                ).classes("w-24")

                ui.button("Cancel", on_click=lambda: naming_dialog.close()).props("color=primary").classes("w-24")

        general_prompt = ui.label("")
        with ui.dialog().classes("h-full") as setting_dialog:
            with ui.card().classes("w-5xl h-full gap-2").style("max-width: none; hax-height: 90vh;"):
                with ui.card().classes("w-full").tight().props("flat bordered"):
                    with ui.card_section().classes("w-full p-2"):
                        with ui.row().classes("w-full items-center gap-2"):
                            ui.label("General system prompt").classes("text-xl")
                            ui.space()

                            self._create_btn = (
                                ui.button("Create new", icon="new_label")
                                .props('size="15px" color="secondary"')
                                .on_click(lambda: naming_dialog.open())
                            )

                            settings_input = (
                                ui.select(
                                    label="Settings name",
                                    options=settings_list_names,
                                    with_input=True,
                                    value=self._interaction_setting.name,
                                    on_change=self.handle_settings_name_change,
                                )
                                .classes("w-64")
                                .props('outlined dense size="15px"')
                            )

                            self._select_btn = (
                                ui.button("Select", icon="check_box")
                                .props('size="15px"')
                                .on_click(lambda: ui.notify(self._selected_interaction_setting))
                            )
                            self._select_btn.visible = False

                            self._save_btn = (
                                ui.button("Save", icon="save")
                                .props('size="15px"')
                                .on_click(lambda: ui.notify(self._selected_interaction_setting))
                            )
                            self._save_btn.visible = False

                            self._cancel_btn = (
                                ui.button("Cancel", icon="cancel")
                                .props('size="15px" color="negative"')
                                .on_click(lambda: ui.notify(self._selected_interaction_setting))
                            )
                            self._cancel_btn.visible = False

                            # ui.button("Add settings", icon="add").props('size="15px"')

                    with ui.element("div").classes("w-full"):
                        self.general_system_prompt = (
                            ui.textarea(
                                label="System prompt",
                                value=self._general_prompt,
                                on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                            )
                            .classes("mx-2 mb-2")
                            .props("outlined input-class='h-full' input-style='resize: none'")
                            .disable()
                        )

                for (
                    n,
                    chatbot_id,
                ) in enumerate(chatbot_ids, start=1):
                    self.files(n, chatbot_id)

        self._setting_dialog = setting_dialog
        self._naming_dialog = naming_dialog

    def handle_settings_name_change(self, e: ValueChangeEventArguments):
        setattr(self, "_selected_interaction_setting", e.value)

        if self._selected_interaction_setting != self._interaction_setting.name:
            self._select_btn.visible = True
        else:
            self._select_btn.visible = False

    def show(self):
        self._setting_dialog.open()

    def hide(self):
        self._setting_dialog.close()

    def files(self, chatbot_number: int, chatbot_id: str):
        test_list = [1, 2, 3, 4, 5, 6]
        test_list = []

        with ui.card().classes("w-full").tight().props("flat bordered"):
            with ui.card_section().classes("w-full p-2"):
                with ui.row().classes("w-full items-center"):
                    ui.label(f"Chatbot #{chatbot_number}").classes("text-xl")
                    ui.space()
                    ui.button("Add files", icon="save").props("outline").disable()

            with ui.grid(columns="3fr 1fr").classes("w-full h-full gap-0"):
                # with ui.scroll_area().classes("w-full h-full"):
                #     ui.codemirror("\n\n\n", language="Markdown").classes("h-full")
                with ui.element("div").classes("mx-2 mb-2"):
                    self._system_prompt_text_area[chatbot_id] = (
                        ui.textarea(
                            label="System prompt",
                            value=self._system_prompt_value[chatbot_id],
                            # placeholder="Write the system prompt",
                            # on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                        )
                        .classes("w-full")
                        .props("outlined input-class='h-full' input-style='resize: none'")
                        .disable()
                    )

                with ui.element("div").classes("mr-2 mb-2 rounded-sm border border-gray-300"):
                    with ui.scroll_area().classes("w-full h-full"):
                        document_list = ui.list().props("separator").classes("m-0 w-full")

                        if not test_list:
                            with ui.item():
                                with ui.item_section():
                                    ui.item_label("No documents found")
                        else:
                            with document_list:
                                for _ in test_list:
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

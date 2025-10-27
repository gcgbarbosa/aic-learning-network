from datetime import datetime

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from src.flow_manager import FlowManager
from src.models.interaction_setting import InteractionSettingsRecord

from loguru import logger


class SettingsModalComponent:
    def __init__(self, flow_manager: FlowManager):
        self._flow_manager = flow_manager

        self._chatbot_prompt_text_area = {}

        interaction = self._flow_manager.get_interaction()
        chatbot_ids = self._flow_manager.get_chatbot_ids()

        self._settings_list = self._flow_manager.list_settings()
        self._settings_list_names = [s.name for s in self._settings_list]

        interaction_setting, chatbot_settings = self._flow_manager.get_interaction_and_chatbot_settings(
            interaction.interaction_settings_id
        )
        self._interaction_setting = (
            interaction_setting  # self.get_interaction_setting(interaction_id=interaction.interaction_settings_id)
        )

        self._chatbot_settings = chatbot_settings

        self._chatbot_system_prompt_value = {
            idx: setting.system_message for idx, setting in self._chatbot_settings.items()
        }

        self._selected_interaction_setting = self._interaction_setting.name

        self._general_system_prompt_value = self._interaction_setting.system_prompt

        self._render_new_settings_dialog()

        with ui.dialog().classes("h-full") as setting_dialog:
            with ui.card().classes("w-5xl h-full gap-2").style("max-width: none; hax-height: 90vh;"):
                self._render_general_settings_card()

                for (
                    n,
                    chatbot_id,
                ) in enumerate(chatbot_ids, start=1):
                    self._render_chatbot_settings_card(n, chatbot_id)

        self._setting_dialog = setting_dialog

    def get_interaction_setting_by_id(self, interaction_id: str) -> InteractionSettingsRecord:
        default_settings = [setting for setting in self._settings_list if setting.id == interaction_id]
        if len(default_settings) != 1:
            raise ValueError("There should be exactly one default settings")
        default_setting = default_settings[-1]

        return default_setting

    def get_interaction_setting_by_name(self, name: str) -> InteractionSettingsRecord:
        default_settings = [setting for setting in self._settings_list if setting.name == name]
        if len(default_settings) != 1:
            raise ValueError(f"There should be exactly one settings with name {name}")
        default_setting = default_settings[-1]

        return default_setting

    def update_prompt_values(self):
        self._general_system_prompt_value = self._general_system_prompt_text_area.value

        for idx, txt_area in self._chatbot_prompt_text_area.items():
            self._chatbot_system_prompt_value[idx] = txt_area.value

    def reset_prompt_values(self):
        self._general_system_prompt_text_area.value = self._general_system_prompt_value

        for idx, text_area in self._chatbot_prompt_text_area.items():
            text_area.value = self._chatbot_system_prompt_value[idx]

    def _handle_cancel_save_new_setting(self):
        settings_name = self._new_settings_name.value

        self._select_btn.visible = False

        self._create_btn.visible = True
        self._save_btn.visible = False
        self._cancel_btn.visible = False

        self._settings_input.enable()

        self._general_system_prompt_text_area.disable()
        for text_area in self._chatbot_prompt_text_area.values():
            text_area.disable()

        self._settings_input.options.remove(settings_name)  # type: ignore[attr-defined]

        self._settings_input.value = self._selected_interaction_setting
        self.reset_prompt_values()

    def _handle_save_new_setting(self):
        name = self._new_settings_name.value
        system_prompt = self._general_system_prompt_text_area.value

        chatbot_settings = []

        for idx, text_area in self._chatbot_prompt_text_area.items():
            chatbot_settings.append(
                {"chatbot_id": idx, "system_message": text_area.value},
            )

        new_interaction_id = self._flow_manager.create_interaction_settings(
            name=name,
            system_prompt=system_prompt,
            chatbot_settings=chatbot_settings,
        )


        self._flow_manager.change_interaction_setting(interaction_settings_id=new_interaction_id)

        self.update_prompt_values()


        self._select_btn.visible = False

        self._create_btn.visible = True
        self._save_btn.visible = False
        self._cancel_btn.visible = False

        self._general_system_prompt_text_area.disable()
        for text_area in self._chatbot_prompt_text_area.values():
            text_area.disable()
        self._settings_input.enable()

        ui.notify("Settings saved", color="positive")

    def _handle_create_new_setting(self):
        settings_name = self._new_settings_name.value

        # check if the setting already exists
        if settings_name.lower() in [d.lower() for d in self._settings_list_names]:
            ui.notify("The name already exists", color="negative")
            return

        self._general_system_prompt_text_area.enable()
        for text_area in self._chatbot_prompt_text_area.values():
            text_area.enable()

        self._naming_dialog.close()

        self._settings_input.disable()
        self._settings_input.options.append(settings_name)  # type: ignore[attr-defined]
        self._settings_input.value = settings_name

        self._select_btn.visible = False
        self._create_btn.visible = False

        self._save_btn.visible = True
        self._cancel_btn.visible = True

    def handle_select_btn_click(self):
        selected_interaction = self._selected_interaction_setting

        setting = self.get_interaction_setting_by_name(selected_interaction)

        self._flow_manager.change_interaction_setting(interaction_settings_id=setting.id)

        self.update_prompt_values()

        self._interaction_setting = setting

        self._select_btn.visible = False

    def handle_settings_name_change(self, e: ValueChangeEventArguments):
        selected_interaction_setting = e.value

        if selected_interaction_setting == self._new_settings_name.value:
            return

        if selected_interaction_setting == self._interaction_setting.name:
            if self._selected_interaction_setting != selected_interaction_setting:
                self._select_btn.visible = False

                setattr(self, "_selected_interaction_setting", selected_interaction_setting)

                self.reset_prompt_values()

            return

        setattr(self, "_selected_interaction_setting", selected_interaction_setting)

        interaction_setting = self.get_interaction_setting_by_name(selected_interaction_setting)

        _, chatbot_settings = self._flow_manager.get_interaction_and_chatbot_settings(interaction_setting.id)

        self._general_system_prompt_text_area.value = interaction_setting.system_prompt

        for idx, setting in chatbot_settings.items():
            self._chatbot_prompt_text_area[idx].value = setting.system_message

        self._select_btn.visible = True

    def show(self):
        self._setting_dialog.open()

    def hide(self):
        self._setting_dialog.close()

    def _render_new_settings_dialog(self):
        with ui.dialog().props("persistent") as self._naming_dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                self._new_settings_name = ui.input("Setting name").classes("w-80")

                with ui.row():
                    ui.button("Confirm", on_click=self._handle_create_new_setting).props(
                        "color=primary",
                    ).classes("w-24")

                    ui.button("Cancel", on_click=lambda: self._naming_dialog.close()).props("color=secondary").classes(
                        "w-24"
                    )

    def _render_general_settings_card(self):
        with ui.card().classes("w-full").tight().props("flat bordered"):
            with ui.card_section().classes("w-full p-2"):
                with ui.row().classes("w-full items-center gap-2"):
                    ui.label("General system prompt").classes("text-xl")
                    ui.space()

                    self._create_btn = (
                        ui.button("Create new", icon="new_label")
                        .props('size="15px" color="secondary"')
                        .on_click(lambda: self._naming_dialog.open())
                    )

                    self._settings_input = (
                        ui.select(
                            label="Settings name",
                            options=self._settings_list_names,
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
                        .on_click(self.handle_select_btn_click)
                    )
                    self._select_btn.visible = False

                    self._save_btn = (
                        ui.button("Save", icon="save").props('size="15px"').on_click(self._handle_save_new_setting)
                    )
                    self._save_btn.visible = False

                    self._cancel_btn = (
                        ui.button("Cancel", icon="cancel")
                        .props('size="15px" color="negative"')
                        .on_click(self._handle_cancel_save_new_setting)
                    )
                    self._cancel_btn.visible = False

                    # ui.button("Add settings", icon="add").props('size="15px"')

            with ui.element("div").classes("w-full"):
                self._general_system_prompt_text_area = (
                    ui.textarea(
                        label="System prompt",
                        value=self._general_system_prompt_value,
                        # on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                    )
                    .classes("mx-2 mb-2")
                    .props("outlined input-class='h-full' input-style='resize: none'")
                )

                self._general_system_prompt_text_area.disable()

    def _render_chatbot_settings_card(self, chatbot_number: int, chatbot_id: str):
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
                    self._chatbot_prompt_text_area[chatbot_id] = (
                        ui.textarea(
                            label="System prompt",
                            value=self._chatbot_system_prompt_value[chatbot_id],
                            # placeholder="Write the system prompt",
                            # on_change=lambda e: general_prompt.set_text("you typed: " + e.value),
                        )
                        .classes("w-full")
                        .props("outlined input-class='h-full' input-style='resize: none'")
                    )

                    self._chatbot_prompt_text_area[chatbot_id].disable()

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

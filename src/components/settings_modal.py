from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from loguru import logger
from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from src.flow_manager import FlowManager
from src.models.chatbot_setting import ChatbotSettingsRecord
from src.models.interaction_setting import InteractionSettingsRecord

BTN_SIZE = 'size="15px"'
BTN_SIZE = ""


class SettingsModalComponent:
    """Modal for viewing/selecting/creating interaction settings.

    WHY: Keep UI state local and expose a tiny public API (show/hide).
    Use small helpers to reduce cognitive load and repetition.
    """

    def __init__(self, flow_manager: FlowManager):
        logger.debug("Initializing SettingsModalComponent")
        self._flow_manager = flow_manager

        self._initialized = False

    def _initialize(self) -> None:
        # --- Data/state caches -------------------------------------------------
        active_interaction = self._flow_manager.get_interaction()
        chatbot_id_list: List[str] = self._flow_manager.get_chatbot_ids()
        logger.debug("Loaded interaction and chatbot ids: {}", chatbot_id_list)

        self._interaction_settings: List[InteractionSettingsRecord] = self._flow_manager.list_settings()
        self._interaction_setting_names: List[str] = [s.name for s in self._interaction_settings]
        logger.debug("Available settings: {}", self._interaction_setting_names)

        current_interaction_setting, chatbot_settings_map = self._flow_manager.get_interaction_and_chatbot_settings(
            active_interaction.interaction_settings_id
        )
        self._current_interaction_setting: InteractionSettingsRecord = current_interaction_setting
        self._chatbot_settings_by_id: Dict[str, ChatbotSettingsRecord] = chatbot_settings_map  # type: ignore[assignment]
        logger.info("Active interaction setting: {}", self._current_interaction_setting.name)

        # Current text values (model) separate from UI widgets (view)
        self._general_prompt_text: str = self._current_interaction_setting.system_prompt
        self._chatbot_prompt_text_by_id: Dict[str, str] = {
            chatbot_id: setting.system_message for chatbot_id, setting in self._chatbot_settings_by_id.items()
        }

        # Currently selected (by name) in the dropdown
        self._selected_interaction_setting_name: str = self._current_interaction_setting.name

        # --- UI widgets (created later) ---------------------------------------
        self._settings_dialog = None
        self._naming_dialog = None

        self._settings_select = None
        self._new_setting_name_input = None

        self._general_prompt_input = None
        self._chatbot_prompt_inputs: Dict[str, ui.textarea] = {}

        self._create_button = None
        self._select_button = None
        self._save_button = None
        self._cancel_button = None

        # --- Build UI ----------------------------------------------------------
        self._build_new_settings_dialog()

        with ui.dialog().classes("h-full") as settings_dialog:
            with ui.card().classes("w-5xl h-full gap-2").style("max-width: none; max-height: 90vh;"):
                self._build_general_settings_card()
                for index, chatbot_id in enumerate(chatbot_id_list, start=1):
                    self._build_chatbot_settings_card(index, chatbot_id)
        self._settings_dialog = settings_dialog
        logger.debug("Settings modal UI created")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def show(self) -> None:
        if self._initialized is False:
            logger.debug("Initializing SettingsModalComponent UI on first show")
            self._initialize()

        if self._settings_dialog:
            logger.debug("Showing SettingsModalComponent dialog")
            self._settings_dialog.open()

    def hide(self) -> None:
        logger.debug("Hiding SettingsModalComponent dialog")
        if self._settings_dialog:
            self._settings_dialog.close()

    # -------------------------------------------------------------------------
    # Lookup helpers
    # -------------------------------------------------------------------------

    def _find_interaction_setting_by_id(self, interaction_id: str) -> InteractionSettingsRecord:
        matches = [s for s in self._interaction_settings if s.id == interaction_id]
        if len(matches) != 1:
            logger.error("Invalid settings count by id {}: {}", interaction_id, len(matches))
            raise ValueError("There should be exactly one default settings")
        return matches[0]

    def _find_interaction_setting_by_name(self, name: str) -> InteractionSettingsRecord:
        matches = [s for s in self._interaction_settings if s.name == name]
        if len(matches) != 1:
            logger.error("Invalid settings count by name {}: {}", name, len(matches))
            raise ValueError(f"There should be exactly one settings with name {name}")
        return matches[0]

    # -------------------------------------------------------------------------
    # State <-> UI sync
    # -------------------------------------------------------------------------

    def _pull_prompts_from_ui(self) -> None:
        if self._general_prompt_input is None:
            raise ValueError("UI not initialized yet")

        self._general_prompt_text = self._general_prompt_input.value
        for chatbot_id, textarea in self._chatbot_prompt_inputs.items():
            self._chatbot_prompt_text_by_id[chatbot_id] = textarea.value
        logger.debug("Pulled prompts from UI")

    def _push_prompts_to_ui(self) -> None:
        if self._general_prompt_input is None:
            raise ValueError("UI not initialized yet")

        self._general_prompt_input.value = self._general_prompt_text
        for chatbot_id, textarea in self._chatbot_prompt_inputs.items():
            textarea.value = self._chatbot_prompt_text_by_id[chatbot_id]
        logger.debug("Pushed prompts to UI")

    # -------------------------------------------------------------------------
    # UI event handlers (renamed for clarity)
    # -------------------------------------------------------------------------

    def _cancel_new_settings(self) -> None:
        if self._new_setting_name_input is None or self._settings_select is None:
            raise ValueError("UI not initialized yet")

        new_setting_name = self._new_setting_name_input.value
        logger.info("Cancelling creation of new settings '{}'", new_setting_name)

        self._toggle_creation_controls(enabled=False)
        self._toggle_prompt_editing(False)
        self._settings_select.enable()

        try:
            self._settings_select.options.remove(new_setting_name)  # type: ignore[attr-defined]
        except ValueError:
            logger.debug("Transient option '{}' not present to remove", new_setting_name)

        self._settings_select.value = self._selected_interaction_setting_name
        self._push_prompts_to_ui()
        self._notify_info("New settings creation canceled; reverted to current selection")

    def _save_new_settings(self) -> None:
        """Persist new setting and switch back to view mode."""
        if self._new_setting_name_input is None or self._general_prompt_input is None or self._settings_select is None:
            raise ValueError("UI not initialized yet")

        new_setting_name = (self._new_setting_name_input.value or "").strip()
        general_prompt_text = self._general_prompt_input.value

        if not new_setting_name:
            self._notify_error("Please enter a name for the settings")
            logger.warning("Attempted to save settings without a name")
            return

        chatbot_settings_payload: List[Dict[str, str]] = [
            {"chatbot_id": chatbot_id, "system_message": textarea.value}
            for chatbot_id, textarea in self._chatbot_prompt_inputs.items()
        ]

        logger.info("Saving new settings '{}'", new_setting_name)
        try:
            new_interaction = self._flow_manager.create_interaction_settings(
                name=new_setting_name,
                system_prompt=general_prompt_text,
                chatbot_settings=chatbot_settings_payload,
            )
            logger.debug("Created settings id {}", new_interaction.id)

            self._flow_manager.change_interaction_setting(interaction_settings_id=new_interaction.id)
            logger.info("Switched active interaction to '{}'", new_setting_name)

            self._pull_prompts_from_ui()  # keep model in sync with UI
            self._toggle_creation_controls(enabled=False)
            self._toggle_prompt_editing(False)
            self._settings_select.enable()

            # Refresh local list (WHY: keep dropdown and cache consistent with backend)
            self._refresh_settings_options()

            self._current_interaction_setting = new_interaction
            self._selected_interaction_setting_name = new_setting_name
            self._new_setting_name_input.value = ""

            self._notify_ok("Settings saved")
        except Exception as exc:
            logger.exception("Failed saving new settings '{}': {}", new_setting_name, exc)
            self._notify_error("Could not save settings. See logs.")

    def _begin_create_new_settings(self) -> None:
        """Transition to 'creating new setting' mode."""
        if self._new_setting_name_input is None or self._naming_dialog is None or self._settings_select is None:
            raise ValueError("UI not initialized yet")

        new_setting_name = (self._new_setting_name_input.value or "").strip()
        if not new_setting_name:
            self._notify_error("Please provide a name")
            logger.warning("Create-new clicked without a name")
            return

        # Guard: disallow duplicates (case-insensitive)
        name_exists = new_setting_name.lower() in (n.lower() for n in self._interaction_setting_names)
        if name_exists:
            self._notify_error("The name already exists")
            logger.warning("Duplicate settings name attempted: '{}'", new_setting_name)
            return

        logger.info("Beginning creation of new settings '{}'", new_setting_name)
        self._naming_dialog.close()

        self._settings_select.disable()
        # Add the new (yet unsaved) option so the select reflects the current editing target.
        self._settings_select.options.append(new_setting_name)  # type: ignore[attr-defined]
        self._settings_select.value = new_setting_name

        self._toggle_creation_controls(enabled=True)
        self._toggle_prompt_editing(True)
        self._notify_info("Editing new settings… don’t forget to Save")

    def _apply_selected_settings(self) -> None:
        if self._select_button is None:
            raise ValueError("UI not initialized yet")

        selected_name = self._selected_interaction_setting_name
        logger.info("Applying selected settings '{}'", selected_name)
        try:
            selected_setting = self._find_interaction_setting_by_name(selected_name)
            self._flow_manager.change_interaction_setting(interaction_settings_id=selected_setting.id)
            self._pull_prompts_from_ui()
            self._current_interaction_setting = selected_setting
            self._select_button.visible = False
            self._notify_ok(f'Applied settings "{selected_name}"')
        except Exception as exc:
            logger.exception("Failed to apply settings '{}': {}", selected_name, exc)
            self._notify_error("Could not apply selected settings")

    def _on_settings_name_changed(self, e: ValueChangeEventArguments) -> None:
        """User picked a different setting in the dropdown."""
        if self._general_prompt_input is None or self._select_button is None:
            raise ValueError("UI not initialized yet")

        new_selection_name: str = e.value
        logger.debug("Dropdown changed to '{}'", new_selection_name)

        is_temp_name = new_selection_name == (
            self._new_setting_name_input.value if self._new_setting_name_input else None
        )
        if is_temp_name:
            logger.debug("Change corresponds to temp name; ignore")
            return

        is_active = new_selection_name == self._current_interaction_setting.name
        changed = self._selected_interaction_setting_name != new_selection_name

        if is_active:
            if changed:
                self._select_button.visible = False
                self._selected_interaction_setting_name = new_selection_name
                self._push_prompts_to_ui()
                logger.debug("Re-selected active settings; prompt values reset to active")
            return

        self._selected_interaction_setting_name = new_selection_name
        try:
            preview_interaction_setting = self._find_interaction_setting_by_name(new_selection_name)
            _, preview_chatbot_settings = self._flow_manager.get_interaction_and_chatbot_settings(
                preview_interaction_setting.id
            )

            self._general_prompt_input.value = preview_interaction_setting.system_prompt
            for chatbot_id, setting in preview_chatbot_settings.items():
                self._chatbot_prompt_inputs[chatbot_id].value = setting.system_message

            self._select_button.visible = True
            self._notify_info(f'Previewing "{new_selection_name}" — click Select to apply')
            logger.debug("Preview loaded for '{}'", new_selection_name)
        except Exception as exc:
            logger.exception("Failed to preview settings '{}': {}", new_selection_name, exc)
            self._notify_error("Could not preview selected settings")

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _build_new_settings_dialog(self) -> None:
        with ui.dialog().props("persistent") as self._naming_dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                self._new_setting_name_input = ui.input("Setting name").classes("w-80")
                with ui.row():
                    ui.button("Confirm", on_click=self._begin_create_new_settings).props(
                        f"color=primary {BTN_SIZE}"
                    ).classes("w-24")
                    ui.button("Cancel", on_click=self._naming_dialog.close).props(
                        f"color=secondary {BTN_SIZE}"
                    ).classes("w-24")
        logger.debug("New settings naming dialog built")

    def _build_general_settings_card(self) -> None:
        if self._naming_dialog is None:
            raise ValueError("UI not initialized yet")

        with ui.card().classes("w-full").tight().props("flat bordered"):
            with ui.card_section().classes("w-full p-2"):
                with ui.row().classes("w-full items-center gap-2"):
                    ui.label("General system prompt").classes("text-xl")
                    ui.space()

                    self._settings_select = (
                        ui.select(
                            label="Settings name",
                            options=self._interaction_setting_names,
                            with_input=True,
                            value=self._current_interaction_setting.name,
                            on_change=self._on_settings_name_changed,
                        )
                        .classes("w-64")
                        .props(f"outlined dense {BTN_SIZE}")
                    )

                    self._create_button = (
                        ui.button("Create new", icon="new_label")
                        .props(f'{BTN_SIZE} color="secondary"')
                        .on_click(self._naming_dialog.open)
                    )

                    self._select_button = (
                        ui.button("Select", icon="check_box").props(BTN_SIZE).on_click(self._apply_selected_settings)
                    )
                    self._select_button.visible = False

                    self._save_button = ui.button("Save", icon="save").props(BTN_SIZE).on_click(self._save_new_settings)
                    self._save_button.visible = False

                    self._cancel_button = (
                        ui.button("Cancel", icon="cancel")
                        .props(f'{BTN_SIZE} color="negative"')
                        .on_click(self._cancel_new_settings)
                    )
                    self._cancel_button.visible = False

            with ui.element("div").classes("w-full"):
                self._general_prompt_input = (
                    ui.textarea(
                        label="System prompt",
                        value=self._general_prompt_text,
                    )
                    .classes("mx-2 mb-2")
                    .props("outlined input-class='h-full' input-style='resize: none'")
                )
                self._general_prompt_input.disable()
        logger.debug("General settings card built")

    def _build_chatbot_settings_card(self, chatbot_index: int, chatbot_id: str) -> None:
        with ui.card().classes("w-full").tight().props("flat bordered"):
            with ui.card_section().classes("w-full p-2"):
                with ui.row().classes("w-full items-center"):
                    ui.label(f"Chatbot #{chatbot_index}").classes("text-xl")
                    ui.space()
                    # WHY: Placeholder button for future file attachments; disabled to communicate intent.
                    ui.button("Add files", icon="save").props("outline").disable()

            with ui.grid(columns="3fr 1fr").classes("w-full h-full gap-0"):
                with ui.element("div").classes("mx-2 mb-2"):
                    self._chatbot_prompt_inputs[chatbot_id] = (
                        ui.textarea(
                            label="System prompt",
                            value=self._chatbot_prompt_text_by_id[chatbot_id],
                        )
                        .classes("w-full")
                        .props("outlined input-class='h-full' input-style='resize: none'")
                    )
                    self._chatbot_prompt_inputs[chatbot_id].disable()

                # Documents pane (empty state for now)
                with ui.element("div").classes("mr-2 mb-2 rounded-sm border border-gray-300"):
                    with ui.scroll_area().classes("w-full h-full"):
                        document_list = ui.list().props("separator").classes("m-0 w-full")
                        with document_list:
                            test_list = []
                            if not test_list:
                                with ui.item():
                                    with ui.item_section():
                                        ui.item_label("No documents found")
                            else:
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
                                            print(upload_date)

                                            ui.item_label(f"{status} • {total_chunks} chunks").props("caption")
                                            # ui.item_label(
                                            #     f"Uploaded: {upload_date.strftime('%Y-%m-%d %H:%M')}"
                                            # ).props("caption")

            # Remove extra padding around scroll content for a tighter look
            ui.query(".q-scrollarea__content").style("padding: 0px")

        logger.debug("Chatbot settings card built for chatbot_id={}", chatbot_id)

    # -------------------------------------------------------------------------
    # Small helpers to cut repetition
    # -------------------------------------------------------------------------

    def _toggle_prompt_editing(self, enabled: bool) -> None:
        if self._general_prompt_input is None:
            raise ValueError("UI not initialized yet")

        if enabled:
            self._general_prompt_input.enable()
            for textarea in self._chatbot_prompt_inputs.values():
                textarea.enable()
            logger.debug("Prompt inputs enabled for editing")
            return

        self._general_prompt_input.disable()
        for textarea in self._chatbot_prompt_inputs.values():
            textarea.disable()
        logger.debug("Prompt inputs disabled for editing")

    def _toggle_creation_controls(self, enabled: bool) -> None:
        if self._select_button is None:
            raise ValueError("UI not initialized yet")
        if self._create_button is None:
            raise ValueError("UI not initialized yet")
        if self._save_button is None:
            raise ValueError("UI not initialized yet")
        if self._cancel_button is None:
            raise ValueError("UI not initialized yet")

        self._select_button.visible = False
        self._create_button.visible = not enabled
        self._save_button.visible = enabled
        self._cancel_button.visible = enabled

        logger.debug("Creation controls set to enabled={}", enabled)

    def _refresh_settings_options(self) -> None:
        """Sync the dropdown options with backend after changes."""
        if self._settings_select is None:
            raise ValueError("UI not initialized yet")

        try:
            self._interaction_settings = self._flow_manager.list_settings()
            self._interaction_setting_names = [s.name for s in self._interaction_settings]
            self._settings_select.options = self._interaction_setting_names  # type: ignore[attr-defined]
            logger.debug("Refreshed settings options: {}", self._interaction_setting_names)
        except Exception as exc:
            logger.exception("Failed to refresh settings options: {}", exc)
            self._notify_error("Could not refresh settings list")

    # -------------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------------

    def _notify_ok(self, message: str) -> None:
        ui.notify(message, color="positive")

    def _notify_error(self, message: str) -> None:
        ui.notify(message, color="negative")

    def _notify_info(self, message: str) -> None:
        ui.notify(message, color="primary")

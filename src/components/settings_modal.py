from __future__ import annotations

from typing import Dict, List

from loguru import logger
from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from src.flow_manager import FlowManager
from src.models.chatbot_setting import ChatbotSettingsRecord
from src.models.interaction_setting import InteractionSettingsRecord

BTN_SIZE = 'size="15px"'


class SettingsModalComponent:
    """Modal for viewing/selecting/creating interaction settings.

    WHY: Keep UI state local and expose a tiny public API (show/hide).
    Use small helpers to reduce cognitive load and repetition.
    """

    def __init__(self, flow_manager: FlowManager):
        logger.debug("Initializing SettingsModalComponent")
        self._flow_manager = flow_manager

        # --- Data/state caches -------------------------------------------------
        interaction = self._flow_manager.get_interaction()
        chatbot_ids: List[str] = self._flow_manager.get_chatbot_ids()
        logger.debug("Loaded interaction and chatbot ids: {}", chatbot_ids)

        self._settings_list: List[InteractionSettingsRecord] = self._flow_manager.list_settings()
        self._settings_list_names: List[str] = [s.name for s in self._settings_list]
        logger.debug("Available settings: {}", self._settings_list_names)

        interaction_setting, chatbot_settings = self._flow_manager.get_interaction_and_chatbot_settings(
            interaction.interaction_settings_id
        )
        self._interaction_setting: InteractionSettingsRecord = interaction_setting
        self._chatbot_settings: Dict[str, ChatbotSettingsRecord] = chatbot_settings  # type: ignore[assignment]
        logger.info("Active interaction setting: {}", self._interaction_setting.name)

        # Current text values (model) separate from UI widgets (view)
        self._general_system_prompt_value: str = self._interaction_setting.system_prompt
        self._chatbot_system_prompt_value: Dict[str, str] = {
            cb_id: setting.system_message for cb_id, setting in self._chatbot_settings.items()
        }

        # Currently selected (by name) in the dropdown
        self._selected_interaction_setting: str = self._interaction_setting.name

        # --- UI widgets (created later) ---------------------------------------
        self._setting_dialog = None
        self._naming_dialog = None

        self._settings_input = None
        self._new_settings_name = None

        self._general_system_prompt_text_area = None
        self._chatbot_prompt_text_area: Dict[str, ui.textarea] = {}

        self._create_btn = None
        self._select_btn = None
        self._save_btn = None
        self._cancel_btn = None

        # --- Build UI ----------------------------------------------------------
        self._build_new_settings_dialog()

        with ui.dialog().classes("h-full") as setting_dialog:
            with ui.card().classes("w-5xl h-full gap-2").style("max-width: none; max-height: 90vh;"):
                self._build_general_settings_card()
                for idx, chatbot_id in enumerate(chatbot_ids, start=1):
                    self._build_chatbot_settings_card(idx, chatbot_id)
        self._setting_dialog = setting_dialog
        logger.debug("Settings modal UI created")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def show(self) -> None:
        logger.debug("Showing SettingsModalComponent dialog")
        if self._setting_dialog:
            self._setting_dialog.open()

    def hide(self) -> None:
        logger.debug("Hiding SettingsModalComponent dialog")
        if self._setting_dialog:
            self._setting_dialog.close()

    # -------------------------------------------------------------------------
    # Lookup helpers
    # -------------------------------------------------------------------------

    def _find_interaction_setting_by_id(self, interaction_id: str) -> InteractionSettingsRecord:
        match = [s for s in self._settings_list if s.id == interaction_id]
        if len(match) != 1:
            logger.error("Invalid settings count by id {}: {}", interaction_id, len(match))
            raise ValueError("There should be exactly one default settings")
        return match[0]

    def _find_interaction_setting_by_name(self, name: str) -> InteractionSettingsRecord:
        match = [s for s in self._settings_list if s.name == name]
        if len(match) != 1:
            logger.error("Invalid settings count by name {}: {}", name, len(match))
            raise ValueError(f"There should be exactly one settings with name {name}")
        return match[0]

    # -------------------------------------------------------------------------
    # State <-> UI sync
    # -------------------------------------------------------------------------

    def _pull_prompts_from_ui(self) -> None:
        if self._general_system_prompt_text_area is None:
            raise ValueError("UI not initialized yet")

        self._general_system_prompt_value = self._general_system_prompt_text_area.value
        for cb_id, txt_area in self._chatbot_prompt_text_area.items():
            self._chatbot_system_prompt_value[cb_id] = txt_area.value
        logger.debug("Pulled prompts from UI")

    def _push_prompts_to_ui(self) -> None:
        if self._general_system_prompt_text_area is None:
            raise ValueError("UI not initialized yet")

        self._general_system_prompt_text_area.value = self._general_system_prompt_value
        for cb_id, text_area in self._chatbot_prompt_text_area.items():
            text_area.value = self._chatbot_system_prompt_value[cb_id]
        logger.debug("Pushed prompts to UI")

    # -------------------------------------------------------------------------
    # UI event handlers (renamed for clarity)
    # -------------------------------------------------------------------------

    def _cancel_new_settings(self) -> None:
        if self._new_settings_name is None or self._settings_input is None:
            raise ValueError("UI not initialized yet")

        settings_name = self._new_settings_name.value
        logger.info("Cancelling creation of new settings '{}'", settings_name)

        self._toggle_creation_controls(enabled=False)
        self._toggle_prompt_editing(False)
        self._settings_input.enable()

        try:
            self._settings_input.options.remove(settings_name)  # type: ignore[attr-defined]
        except ValueError:
            logger.debug("Transient option '{}' not present to remove", settings_name)

        self._settings_input.value = self._selected_interaction_setting
        self._push_prompts_to_ui()
        self._notify_info("New settings creation canceled; reverted to current selection")

    def _save_new_settings(self) -> None:
        """Persist new setting and switch back to view mode."""
        if (
            self._new_settings_name is None
            or self._general_system_prompt_text_area is None
            or self._settings_input is None
        ):
            raise ValueError("UI not initialized yet")

        name = (self._new_settings_name.value or "").strip()
        system_prompt = self._general_system_prompt_text_area.value

        if not name:
            self._notify_error("Please enter a name for the settings")
            logger.warning("Attempted to save settings without a name")
            return

        chatbot_settings_payload: List[Dict[str, str]] = [
            {"chatbot_id": cb_id, "system_message": text_area.value}
            for cb_id, text_area in self._chatbot_prompt_text_area.items()
        ]

        logger.info("Saving new settings '{}'", name)
        try:
            new_interaction_id = self._flow_manager.create_interaction_settings(
                name=name,
                system_prompt=system_prompt,
                chatbot_settings=chatbot_settings_payload,
            )
            logger.debug("Created settings id {}", new_interaction_id)

            self._flow_manager.change_interaction_setting(interaction_settings_id=new_interaction_id)
            logger.info("Switched active interaction to '{}'", name)

            self._pull_prompts_from_ui()  # keep model in sync with UI
            self._toggle_creation_controls(enabled=False)
            self._toggle_prompt_editing(False)
            self._settings_input.enable()

            # Refresh local list (WHY: keep dropdown and cache consistent with backend)
            self._refresh_settings_options()

            self._notify_ok("Settings saved")
        except Exception as exc:
            logger.exception("Failed saving new settings '{}': {}", name, exc)
            self._notify_error("Could not save settings. See logs.")

    def _begin_create_new_settings(self) -> None:
        """Transition to 'creating new setting' mode."""
        if self._new_settings_name is None or self._naming_dialog is None or self._settings_input is None:
            raise ValueError("UI not initialized yet")

        settings_name = (self._new_settings_name.value or "").strip()
        if not settings_name:
            self._notify_error("Please provide a name")
            logger.warning("Create-new clicked without a name")
            return

        # Guard: disallow duplicates (case-insensitive)
        name_exists = settings_name.lower() in (n.lower() for n in self._settings_list_names)
        if name_exists:
            self._notify_error("The name already exists")
            logger.warning("Duplicate settings name attempted: '{}'", settings_name)
            return

        logger.info("Beginning creation of new settings '{}'", settings_name)
        self._naming_dialog.close()

        self._settings_input.disable()
        # Add the new (yet unsaved) option so the select reflects the current editing target.
        self._settings_input.options.append(settings_name)  # type: ignore[attr-defined]
        self._settings_input.value = settings_name

        self._toggle_creation_controls(enabled=True)
        self._toggle_prompt_editing(True)
        self._notify_info("Editing new settings… don’t forget to Save")

    def _apply_selected_settings(self) -> None:
        if self._select_btn is None:
            raise ValueError("UI not initialized yet")

        selected_name = self._selected_interaction_setting
        logger.info("Applying selected settings '{}'", selected_name)
        try:
            setting = self._find_interaction_setting_by_name(selected_name)
            self._flow_manager.change_interaction_setting(interaction_settings_id=setting.id)
            self._pull_prompts_from_ui()
            self._interaction_setting = setting
            self._select_btn.visible = False
            self._notify_ok(f'Applied settings "{selected_name}"')
        except Exception as exc:
            logger.exception("Failed to apply settings '{}': {}", selected_name, exc)
            self._notify_error("Could not apply selected settings")

    def _on_settings_name_changed(self, e: ValueChangeEventArguments) -> None:
        """User picked a different setting in the dropdown."""
        if self._general_system_prompt_text_area is None or self._select_btn is None:
            raise ValueError("UI not initialized yet")

        new_selection: str = e.value
        logger.debug("Dropdown changed to '{}'", new_selection)

        is_temp_name = new_selection == (self._new_settings_name.value if self._new_settings_name else None)
        if is_temp_name:
            logger.debug("Change corresponds to temp name; ignore")
            return

        is_active = new_selection == self._interaction_setting.name
        changed = self._selected_interaction_setting != new_selection

        if is_active:
            if changed:
                self._select_btn.visible = False
                self._selected_interaction_setting = new_selection
                self._push_prompts_to_ui()
                logger.debug("Re-selected active settings; prompt values reset to active")
            return

        self._selected_interaction_setting = new_selection
        try:
            interaction_setting = self._find_interaction_setting_by_name(new_selection)
            _, chatbot_settings = self._flow_manager.get_interaction_and_chatbot_settings(interaction_setting.id)

            self._general_system_prompt_text_area.value = interaction_setting.system_prompt
            for cb_id, setting in chatbot_settings.items():
                self._chatbot_prompt_text_area[cb_id].value = setting.system_message

            self._select_btn.visible = True
            self._notify_info(f'Previewing "{new_selection}" — click Select to apply')
            logger.debug("Preview loaded for '{}'", new_selection)
        except Exception as exc:
            logger.exception("Failed to preview settings '{}': {}", new_selection, exc)
            self._notify_error("Could not preview selected settings")

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _build_new_settings_dialog(self) -> None:
        with ui.dialog().props("persistent") as self._naming_dialog:
            with ui.card().style("max-width: none").classes("p-10 pr-14"):
                self._new_settings_name = ui.input("Setting name").classes("w-80")
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

                    self._create_btn = (
                        ui.button("Create new", icon="new_label")
                        .props(f'{BTN_SIZE} color="secondary"')
                        .on_click(self._naming_dialog.open)
                    )

                    self._settings_input = (
                        ui.select(
                            label="Settings name",
                            options=self._settings_list_names,
                            with_input=True,
                            value=self._interaction_setting.name,
                            on_change=self._on_settings_name_changed,
                        )
                        .classes("w-64")
                        .props(f"outlined dense {BTN_SIZE}")
                    )

                    self._select_btn = (
                        ui.button("Select", icon="check_box").props(BTN_SIZE).on_click(self._apply_selected_settings)
                    )
                    self._select_btn.visible = False

                    self._save_btn = ui.button("Save", icon="save").props(BTN_SIZE).on_click(self._save_new_settings)
                    self._save_btn.visible = False

                    self._cancel_btn = (
                        ui.button("Cancel", icon="cancel")
                        .props(f'{BTN_SIZE} color="negative"')
                        .on_click(self._cancel_new_settings)
                    )
                    self._cancel_btn.visible = False

            with ui.element("div").classes("w-full"):
                self._general_system_prompt_text_area = (
                    ui.textarea(
                        label="System prompt",
                        value=self._general_system_prompt_value,
                    )
                    .classes("mx-2 mb-2")
                    .props("outlined input-class='h-full' input-style='resize: none'")
                )
                self._general_system_prompt_text_area.disable()
        logger.debug("General settings card built")

    def _build_chatbot_settings_card(self, chatbot_number: int, chatbot_id: str) -> None:
        with ui.card().classes("w-full").tight().props("flat bordered"):
            with ui.card_section().classes("w-full p-2"):
                with ui.row().classes("w-full items-center"):
                    ui.label(f"Chatbot #{chatbot_number}").classes("text-xl")
                    ui.space()
                    # WHY: Placeholder button for future file attachments; disabled to communicate intent.
                    ui.button("Add files", icon="save").props("outline").disable()

            with ui.grid(columns="3fr 1fr").classes("w-full h-full gap-0"):
                with ui.element("div").classes("mx-2 mb-2"):
                    self._chatbot_prompt_text_area[chatbot_id] = (
                        ui.textarea(
                            label="System prompt",
                            value=self._chatbot_system_prompt_value[chatbot_id],
                        )
                        .classes("w-full")
                        .props("outlined input-class='h-full' input-style='resize: none'")
                    )
                    self._chatbot_prompt_text_area[chatbot_id].disable()

                # Documents pane (empty state for now)
                with ui.element("div").classes("mr-2 mb-2 rounded-sm border border-gray-300"):
                    with ui.scroll_area().classes("w-full h-full"):
                        document_list = ui.list().props("separator").classes("m-0 w-full")
                        with document_list:
                            with ui.item():
                                with ui.item_section():
                                    ui.item_label("No documents found")

            # Remove extra padding around scroll content for a tighter look
            ui.query(".q-scrollarea__content").style("padding: 0px")
        logger.debug("Chatbot settings card built for chatbot_id={}", chatbot_id)

    # -------------------------------------------------------------------------
    # Small helpers to cut repetition
    # -------------------------------------------------------------------------

    def _toggle_prompt_editing(self, enabled: bool) -> None:
        if self._general_system_prompt_text_area is None:
            raise ValueError("UI not initialized yet")

        if enabled:
            self._general_system_prompt_text_area.enable()
            for ta in self._chatbot_prompt_text_area.values():
                ta.enable()
            logger.debug("Prompt inputs enabled for editing")
            return

        self._general_system_prompt_text_area.disable()
        for ta in self._chatbot_prompt_text_area.values():
            ta.disable()
        logger.debug("Prompt inputs disabled for editing")

    def _toggle_creation_controls(self, enabled: bool) -> None:
        if self._select_btn is None:
            raise ValueError("UI not initialized yet")

        if self._create_btn is None:
            raise ValueError("UI not initialized yet")

        if self._save_btn is None:
            raise ValueError("UI not initialized yet")

        if self._cancel_btn is None:
            raise ValueError("UI not initialized yet")

        self._select_btn.visible = False
        self._create_btn.visible = not enabled
        self._save_btn.visible = enabled
        self._cancel_btn.visible = enabled

        logger.debug("Creation controls set to enabled={}", enabled)

    def _refresh_settings_options(self) -> None:
        """Sync the dropdown options with backend after changes."""
        if self._settings_input is None:
            raise ValueError("UI not initialized yet")

        try:
            self._settings_list = self._flow_manager.list_settings()
            self._settings_list_names = [s.name for s in self._settings_list]
            self._settings_input.options = self._settings_list_names  # type: ignore[attr-defined]
            logger.debug("Refreshed settings options: {}", self._settings_list_names)
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

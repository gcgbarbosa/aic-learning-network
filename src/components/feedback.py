from nicegui import ui
from nicegui.elements.row import Row

from src.flow_manager import FlowManager

import json


class FeedbackComponent:
    def __init__(self, flow_manager: FlowManager):
        self._error_signs = {}
        self._error_box_classes = "border border-red-300 p-4 rounded-sm"

        self._flow_manager = flow_manager

        with ui.row().classes("w-full") as row:
            with ui.column().classes("mx-4 p-8 w-full border border-gray-300 rounded-sm gap-4"):
                ui.label("Feedback Survey").classes("text-lg font-bold")

                self.result = {
                    # stars
                    "rate1": 0,
                    "rate2": 0,
                    "rate3": 0,
                    # select
                    "professional_preference": None,
                    "best_referral": None,
                    "seekers_preference": None,
                    # open
                    "professional_reason": "",
                    "referral_timing": "",
                    "seekers_reason": "",
                    "other_remarks": "",
                    "chat_snippet": "",
                }

                self.error_box = ui.column().classes("hidden")

                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    # ratings
                    ui.label("Rating: hoeveel sterren geef je elk van de drie chatbots").classes("font-semibold mb-2")

                    with ui.row().classes("items-center gap-8"):
                        with ui.column().classes("gap-1"):
                            ui.label("Chatbot #1").classes("text-sm font-medium")
                            ui.rating(value=0, max=5, size="lg", icon="star", icon_selected="star").bind_value_to(
                                self.result, "rate1"
                            ).on_value_change(self._check_errors)

                        with ui.column().classes("gap-1"):
                            ui.label("Chatbot #2").classes("text-sm font-medium")
                            ui.rating(value=0, max=5, size="lg", icon="star", icon_selected="star").bind_value_to(
                                self.result, "rate2"
                            ).on_value_change(self._check_errors)

                        with ui.column().classes("gap-1"):
                            ui.label("Chatbot #3").classes("text-sm font-medium")
                            ui.rating(value=0, max=5, size="lg", icon="star", icon_selected="star").bind_value_to(
                                self.result, "rate3"
                            ).on_value_change(self._check_errors)

                    label = ui.label("Please select a star for each chatbot").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["ratings"] = (box, label)

                # ratings.classes.clear()
                ui.separator()

                # preferences

                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    ui.label(
                        "Welke van de chatbots heeft je voorkeur vanuit de positie van professional? (verplicht)"
                    ).classes("font-semibold")

                    self.prof_pref = (
                        ui.radio(options=["Chatbot 1", "Chatbot 2", "Chatbot 3", "weet niet"])
                        .classes("w-full max-w-xl")
                        .props("inline")
                        .bind_value_to(self.result, "professional_preference")
                        .on_value_change(self._check_errors)
                    )

                    label = ui.label("Please select one option").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["professional_preference"] = (box, label)

                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    ui.label(
                        "Wat maakt dat jij, als professional, deze chatbot verkiest? Leg uit waarom (verplicht)"
                    ).classes("font-semibold mb-4")

                    self.prof_reason = (
                        ui.textarea(placeholder="Beschrijf je motivatie...")
                        .props("outlined autogrow counter maxlength=600 rows=3")
                        .classes("w-full")
                        .bind_value_to(self.result, "professional_reason")
                        .on_value_change(self._check_errors)
                    )

                    label = ui.label("Please provide a reason").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["professional_reason"] = (box, label)

                ui.separator()

                # best
                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    ui.label(
                        "Welke chatbot heeft het beste doorverwezen naar menselijke hulp volgens jou? (verplicht)"
                    ).classes("font-semibold")

                    self.best_ref = (
                        ui.radio(options=["Chatbot 1", "Chatbot 2", "Chatbot 3", "weet niet"])
                        .classes("w-full max-w-xl")
                        .props("inline")
                        .bind_value_to(self.result, "best_referral")
                        .on_value_change(self._check_errors)
                    )

                    label = ui.label("Please select one option").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["best_referral"] = (box, label)

                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    ui.label(
                        "Terugkijkend: op welk moment in chatgesprekken moet er best doorverwezen worden naar "
                        "menselijke hulp bij gevoelige onderwerpen? (verplicht)"
                    ).classes("font-semibold mb-4")

                    self.ref_timing = (
                        ui.textarea(placeholder="Beschrijf het ideale moment of de signalen...")
                        .props("outlined autogrow counter maxlength=600 rows=3")
                        .classes("w-full")
                        .bind_value_to(self.result, "referral_timing")
                        .on_value_change(self._check_errors)
                    )

                    label = ui.label("Please provide timing information").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["referral_timing"] = (box, label)

                ui.separator()

                # seeker's perspective
                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    ui.label(
                        "Vanuit het perspectief van hulpzoekers (zoals jongeren): welke chatbot zouden zij prefereren? "
                        "(verplicht)"
                    ).classes("font-semibold")

                    self.seekers_pref = (
                        ui.radio(options=["Chatbot 1", "Chatbot 2", "Chatbot 3", "weet niet"])
                        .classes("w-full max-w-xl")
                        .props("inline")
                        .bind_value_to(self.result, "seekers_preference")
                        .on_value_change(self._check_errors)
                    )

                    label = ui.label("Please select one option").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["seekers_preference"] = (box, label)

                with ui.element("div").classes("w-full lg:w-2/3") as box:
                    ui.label(
                        "Wat maakt dat je denkt dat hulpzoekers deze chatbot zouden verkiezen? "
                        "Hoe zouden zij kijken naar zo'n doorverwijzing? (verplicht)"
                    ).classes("font-semibold mb-4")

                    self.seekers_reason = (
                        ui.textarea(placeholder="Leg je redenering uit...")
                        .props("outlined autogrow counter maxlength=600 rows=3")
                        .classes("w-full")
                        .bind_value_to(self.result, "seekers_reason")
                        .on_value_change(self._check_errors)
                    )

                    label = ui.label("Please provide your reasoning").classes("text-red-600 text-sm mt-4")
                    label.visible = False

                self._error_signs["seekers_reason"] = (box, label)

                ui.separator()

                # others
                ui.label("Heb je nog andere bedenkingen of ideeën over deze chatgesprekken? (optioneel)").classes(
                    "font-semibold"
                )
                self.other = (
                    ui.textarea(placeholder="Andere opmerkingen...")
                    .props("outlined autogrow counter maxlength=600 rows=3")
                    .classes("w-full lg:w-2/3")
                    .bind_value_to(self.result, "other_remarks")
                )

                ui.label(
                    "Als je wil, kan je hieronder een deel van het chatgesprek plakken en kort toelichten "
                    "wat je wil verduidelijken. (optioneel)"
                ).classes("font-semibold")
                self.snippet = (
                    ui.textarea(placeholder="Plak hier een fragment en licht toe...")
                    .props("outlined autogrow counter maxlength=1200 rows=5")
                    .classes("w-full lg:w-2/3")
                    .bind_value_to(self.result, "chat_snippet")
                )

                with ui.row().classes("gap-3 mt-2"):
                    ui.button("Verzend feedback", on_click=self._submit).classes("btn-primary")

        self._row = row

    def _show_errors(self, field: str):
        self._error_signs[field][0].classes(add=self._error_box_classes)
        self._error_signs[field][1].visible = True

    def _hide_errors(self, field: str):
        self._error_signs[field][0].classes(remove=self._error_box_classes)
        self._error_signs[field][1].visible = False

    def _check_errors(self):
        if self.result["rate1"] != 0 and self.result["rate2"] != 0 and self.result["rate3"] != 0:
            self._hide_errors("ratings")

        if self.result["professional_preference"] is not None:
            self._hide_errors("professional_preference")

        if self.result["professional_reason"].strip():
            self._hide_errors("professional_reason")

        if self.result["best_referral"] is not None:
            self._hide_errors("best_referral")

        if self.result["referral_timing"].strip():
            self._hide_errors("referral_timing")

        if self.result["seekers_preference"] is not None:
            self._hide_errors("seekers_preference")

        if self.result["seekers_reason"].strip():
            self._hide_errors("seekers_reason")

    def _submit(self):
        errors_found = False

        if self.result["rate1"] == 0 or self.result["rate2"] == 0 or self.result["rate3"] == 0:
            self._show_errors("ratings")
            errors_found = True

        if self.result["professional_preference"] is None:
            self._show_errors("professional_preference")
            errors_found = True

        if not self.result["professional_reason"].strip():
            self._show_errors("professional_reason")
            errors_found = True

        if self.result["best_referral"] is None:
            self._show_errors("best_referral")
            errors_found = True

        if not self.result["referral_timing"].strip():
            self._show_errors("referral_timing")
            errors_found = True

        if self.result["seekers_preference"] is None:
            self._show_errors("seekers_preference")
            errors_found = True

        if not self.result["seekers_reason"].strip():
            self._show_errors("seekers_reason")
            errors_found = True

        if errors_found:
            ui.notify(self.result)
            return

        ui.notify("Bedankt voor je feedback!", type="positive")
        # TODO: go to thank you page
        self._flow_manager.submit_user_feedback(json.dumps(self.result))

    def element(self) -> Row:
        return self._row

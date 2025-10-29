from nicegui import ui
from nicegui.elements.row import Row


class FeedbackComponent:
    def __init__(self):
        with ui.row().classes("w-full") as row:
            with ui.column().classes("mx-4 p-8 w-full border border-gray-300 rounded-sm gap-5"):
                ui.label("Feedback Survey").classes("text-lg font-bold")

                # Central state
                self.result = {
                    # Ratings (0–5 allowed)
                    "rate1": 0,
                    "rate2": 0,
                    "rate3": 0,
                    # Single choice
                    "professional_preference": None,
                    "best_referral": None,
                    "seekers_preference": None,
                    # Open text
                    "professional_reason": "",
                    "referral_timing": "",
                    "seekers_reason": "",
                    "other_remarks": "",
                    "chat_snippet": "",
                }

                # A place to show validation errors
                self.error_box = ui.column().classes("hidden")

                # ------------------ Ratings ------------------
                ui.label("Rating: hoeveel sterren geef je elk van de drie chatbots").classes("font-semibold")
                ui.label("Kies voor elke chatbot 0 tot 5 sterren.").classes("text-xs text-gray-500")

                with ui.row().classes("items-center gap-8"):
                    with ui.column().classes("gap-1"):
                        ui.label("Chatbot #1").classes("text-sm font-medium")
                        ui.rating(value=0, max=5, size="lg", icon="star", icon_selected="star").bind_value_to(
                            self.result, "rate1"
                        )

                    with ui.column().classes("gap-1"):
                        ui.label("Chatbot #2").classes("text-sm font-medium")
                        ui.rating(value=0, max=5, size="lg", icon="star", icon_selected="star").bind_value_to(
                            self.result, "rate2"
                        )

                    with ui.column().classes("gap-1"):
                        ui.label("Chatbot #3").classes("text-sm font-medium")
                        ui.rating(value=0, max=5, size="lg", icon="star", icon_selected="star").bind_value_to(
                            self.result, "rate3"
                        )

                ui.separator()

                # ------------------ Professional preference ------------------
                ui.label(
                    "Welke van de chatbots heeft je voorkeur vanuit de positie van professional? (verplicht)"
                ).classes("font-semibold")
                ui.label("Kies precies één optie.").classes("text-xs text-gray-500")

                self.prof_pref = (
                    ui.radio(options=["Chatbot 1", "Chatbot 2", "Chatbot 3", "weet niet"])
                    .classes("w-full max-w-xl")
                    .props("inline")
                    .bind_value_to(self.result, "professional_preference")
                )

                ui.label(
                    "Wat maakt dat jij, als professional, deze chatbot verkiest? Leg uit waarom (verplicht)"
                ).classes("font-semibold")
                ui.label("Schrijf kort en duidelijk.").classes("text-xs text-gray-500")

                self.prof_reason = (
                    ui.textarea(placeholder="Beschrijf je motivatie...")
                    .props("outlined autogrow counter maxlength=600 rows=3")
                    .classes("w-full")
                    .bind_value_to(self.result, "professional_reason")
                )

                ui.separator()

                # ------------------ Best referral to human help ------------------
                ui.label(
                    "Welke chatbot heeft het beste doorverwezen naar menselijke hulp volgens jou? (verplicht)"
                ).classes("font-semibold")
                ui.label("Kies precies één optie.").classes("text-xs text-gray-500")

                self.best_ref = (
                    ui.radio(options=["Chatbot 1", "Chatbot 2", "Chatbot 3", "weet niet"])
                    .classes("w-full max-w-xl")
                    .props("inline")
                    .bind_value_to(self.result, "best_referral")
                )

                ui.label(
                    "Terugkijkend: op welk moment in chatgesprekken moet er best doorverwezen worden naar "
                    "menselijke hulp bij gevoelige onderwerpen? (verplicht)"
                ).classes("font-semibold")
                ui.label("Noem signalen of situaties waarin doorverwijzen aangewezen is.").classes(
                    "text-xs text-gray-500"
                )

                self.ref_timing = (
                    ui.textarea(placeholder="Beschrijf het ideale moment of de signalen...")
                    .props("outlined autogrow counter maxlength=600 rows=3")
                    .classes("w-full")
                    .bind_value_to(self.result, "referral_timing")
                )

                ui.separator()

                # ------------------ Seekers’ perspective ------------------
                ui.label(
                    "Vanuit het perspectief van hulpzoekers (zoals jongeren): welke chatbot zouden zij prefereren? "
                    "(verplicht)"
                ).classes("font-semibold")
                ui.label("Kies precies één optie.").classes("text-xs text-gray-500")

                self.seekers_pref = (
                    ui.radio(options=["Chatbot 1", "Chatbot 2", "Chatbot 3", "weet niet"])
                    .classes("w-full max-w-xl")
                    .props("inline")
                    .bind_value_to(self.result, "seekers_preference")
                )

                ui.label(
                    "Wat maakt dat je denkt dat hulpzoekers deze chatbot zouden verkiezen? "
                    "Hoe zouden zij kijken naar zo’n doorverwijzing? (verplicht)"
                ).classes("font-semibold")
                ui.label("Licht je redenering toe.").classes("text-xs text-gray-500")

                self.seekers_reason = (
                    ui.textarea(placeholder="Leg je redenering uit...")
                    .props("outlined autogrow counter maxlength=600 rows=3")
                    .classes("w-full")
                    .bind_value_to(self.result, "seekers_reason")
                )

                ui.separator()

                # ------------------ Other remarks & snippet ------------------
                ui.label("Heb je nog andere bedenkingen of ideeën over deze chatgesprekken? (optioneel)").classes(
                    "font-semibold"
                )
                self.other = (
                    ui.textarea(placeholder="Andere opmerkingen...")
                    .props("outlined autogrow counter maxlength=600 rows=3")
                    .classes("w-full")
                    .bind_value_to(self.result, "other_remarks")
                )

                ui.label(
                    "Als je wil, kan je hieronder een deel van het chatgesprek plakken en kort toelichten "
                    "wat je wil verduidelijken. (optioneel)"
                ).classes("font-semibold")
                self.snippet = (
                    ui.textarea(placeholder="Plak hier een fragment en licht toe...")
                    .props("outlined autogrow counter maxlength=1200 rows=5")
                    .classes("w-full")
                    .bind_value_to(self.result, "chat_snippet")
                )

                # ------------------ Actions ------------------
                with ui.row().classes("gap-3 mt-2"):
                    submit_button = ui.button("Verzend feedback", on_click=self._submit).classes("btn-primary")
                    ui.button("Leeg formulier", on_click=self._reset).props("flat")

        self._row = row

    # ---------- Helpers ----------
    def _reset(self):
        # reset all fields
        self.result.update(
            {
                "rate1": 0,
                "rate2": 0,
                "rate3": 0,
                "professional_preference": None,
                "best_referral": None,
                "seekers_preference": None,
                "professional_reason": "",
                "referral_timing": "",
                "seekers_reason": "",
                "other_remarks": "",
                "chat_snippet": "",
            }
        )
        ui.notify("Formulier leeggemaakt.")
        # re-render counters/values
        for el in (
            self.prof_pref,
            self.best_ref,
            self.seekers_pref,
            self.prof_reason,
            self.ref_timing,
            self.seekers_reason,
            self.other,
            self.snippet,
        ):
            el.update()
        # hide errors again
        self._show_errors([])

    def _submit(self):
        errors = []

        # required single-choice
        if not self.result["professional_preference"]:
            errors.append("Kies je voorkeur als professional.")
        if not self.result["best_referral"]:
            errors.append("Kies welke chatbot het best doorverwees naar menselijke hulp.")
        if not self.result["seekers_preference"]:
            errors.append("Kies welke chatbot hulpzoekers zouden prefereren.")

        # required open text (non-empty, min length)
        def short(text: str) -> bool:
            return len(text.strip()) >= 10  # minimal nuttige toelichting

        if not short(self.result["professional_reason"]):
            errors.append("Leg kort uit waarom je als professional deze chatbot verkiest (min. 10 tekens).")
        if not short(self.result["referral_timing"]):
            errors.append("Beschrijf wanneer best doorverwezen wordt (min. 10 tekens).")
        if not short(self.result["seekers_reason"]):
            errors.append("Leg uit waarom hulpzoekers deze chatbot zouden kiezen (min. 10 tekens).")

        if errors:
            self._show_errors(errors)
            ui.notify("Controleer het formulier: sommige verplichte velden ontbreken.", type="warning")
            return

        # All good
        self._show_errors([])
        print("Feedback payload:", self.result)  # replace by persistence layer
        ui.notify("Bedankt voor je feedback!", type="positive")

    def _show_errors(self, messages: list[str]):
        # Simple error list at the top; show/hide + render bullets
        self.error_box.clear()
        if messages:
            self.error_box.classes(remove="hidden")
            with self.error_box:
                ui.label("Gelieve de volgende punten te vervolledigen:").classes("text-red-600 font-semibold")
                for msg in messages:
                    ui.label(f"• {msg}").classes("text-red-600")
        else:
            self.error_box.classes(add="hidden")

    def element(self) -> Row:
        return self._row

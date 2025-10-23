"""Entrypoint"""

from nicegui import app, ui
from components import HeaderComponent, FooterComponent, MessagesComponent


@ui.page("/")
def main():
    """
    Main function that prints a greeting message and returns the sum of 1 and 1.

    This function outputs a simple greeting to the console and computes a basic arithmetic
    operation.

    Returns:
        int: The result of the arithmetic operation (1 + 1), which is 2.
    """

    HeaderComponent()

    MessagesComponent()

    FooterComponent()


if __name__ in {"__main__", "__mp_main__"}:

    ui.run(storage_secret="THIS_NEEDS_TO_BE_CHANGED", port=8880)

from nicegui import binding


class TimerModel:
    remaining = binding.BindableProperty()

    def __init__(self, start_value: int):
        self.remaining = start_value

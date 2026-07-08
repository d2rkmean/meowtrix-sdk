from .base_filter import BaseFilter

class Command(BaseFilter):

    def __init__(self, name: str) -> None:
        self.name = f"!{name}"

    def __call__(self, event) -> bool:
        body = getattr(event.content, "body", "") or ""
        return body == self.name or body.startswith(self.name + " ")
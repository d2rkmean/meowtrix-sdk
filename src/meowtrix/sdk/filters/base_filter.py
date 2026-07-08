from typing import Callable, Union

from ..types.events.base_event import BaseEvent

Filter = Callable[[BaseEvent], bool]
FilterLike = Union[Filter, "BaseFilter"]


class BaseFilter:
    def __call__(self, event: BaseEvent) -> bool:
        raise NotImplementedError

    def __and__(self, other: "FilterLike") -> "BaseFilter":
        return _AndFilter(self, other)

    def __or__(self, other: "FilterLike") -> "BaseFilter":
        return _OrFilter(self, other)

    def __invert__(self) -> "BaseFilter":
        return _NotFilter(self)


class _AndFilter(BaseFilter):
    def __init__(self, left: FilterLike, right: FilterLike) -> None:
        self.left = left
        self.right = right

    def __call__(self, event: BaseEvent) -> bool:
        return self.left(event) and self.right(event)


class _OrFilter(BaseFilter):
    def __init__(self, left: FilterLike, right: FilterLike) -> None:
        self.left = left
        self.right = right

    def __call__(self, event: BaseEvent) -> bool:
        return self.left(event) or self.right(event)


class _NotFilter(BaseFilter):
    def __init__(self, inner: FilterLike) -> None:
        self.inner = inner

    def __call__(self, event: BaseEvent) -> bool:
        return not self.inner(event)


def apply_filters(event: BaseEvent, filters: list[FilterLike]) -> bool:
    return all(f(event) for f in filters)
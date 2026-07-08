from dataclasses import dataclass, fields, asdict, is_dataclass, field, MISSING
from typing import Any, ClassVar, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from .relations import RelatesTo, Mentions
if TYPE_CHECKING:
    from ...bot import Bot


@dataclass
class BaseContent:
    relates_to: Optional["RelatesTo"] = field(default=None, repr=False)
    mentions: Optional["Mentions"] = field(default=None, repr=False)
    extra: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(kw_only=True)
class BaseEvent(ABC):
    room_id: str | None = None
    event_id: str | None = None
    sender_id: str | None = None
    bot: "Bot" = field(repr=False, compare=False, default=None)
    event_type: Optional[str] = None
    content: Optional[BaseContent] = None
    raw: Optional[dict[str, Any]] = None

    _registry: ClassVar[list[type["BaseEvent"]]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "filter" in cls.__dict__:
            BaseEvent._registry.append(cls)

    @staticmethod
    @abstractmethod
    def filter(data: dict[str, Any]) -> bool:
        raise NotImplementedError

    @classmethod
    def content_class(cls) -> type[BaseContent]:
        content_field = next(f for f in fields(cls) if f.name == "content")
        content_type = content_field.type
        if isinstance(content_type, str):
            raise TypeError(
                f"content field type is a string ('{content_type}'); "
                f"avoid `from __future__ import annotations` here or override content_class()."
            )
        return content_type

    @classmethod
    def from_dict(cls, data: dict[str, Any], bot: "Bot") -> "BaseEvent":
        if cls is BaseEvent:
            for candidate in cls._registry:
                if candidate.filter(data):
                    return candidate.from_dict(data, bot)
            raise ValueError(f"No matching event class for data: {data}")

        content_data = dict(data.get("content", {})) 
        content_cls = cls.content_class()
        known_names = {f.name for f in fields(content_cls) if f.name != "extra"}

        known_kwargs = {
            f.name: content_data.get(f.name)
            for f in fields(content_cls)
            if f.name != "extra" and (f.name in content_data or _has_default(f))
        }
        extra_kwargs = {k: v for k, v in content_data.items() if k not in known_names}

        content_obj = content_cls(**known_kwargs, extra=extra_kwargs)

        return cls(
            room_id=data["room_id"],
            event_id=data["event_id"],
            sender_id=data["sender"],
            bot=bot,
            event_type=data.get("type"),
            content=content_obj,
            raw=data,
        )

    def to_dict(self) -> dict[str, Any]:
        content_dict: dict[str, Any] = {}
        if is_dataclass(self.content):
            content_dict = {
                k: v for k, v in asdict(self.content).items()
                if k not in ("extra", "relates_to", "mentions") and v is not None
            }
            if self.content.relates_to:
                content_dict["m.relates_to"] = self.content.relates_to.to_dict()
            if self.content.mentions:
                content_dict["m.mentions"] = self.content.mentions.to_dict()
            content_dict.update(getattr(self.content, "extra", {}) or {})
        elif self.content is not None:
            content_dict = self.content

        result = dict(self.raw) if self.raw else {}
        result.update({
            "type": self.event_type,
            "room_id": self.room_id,
            "event_id": self.event_id,
            "sender": self.sender_id,
            "content": content_dict,
        })
        return result


def _has_default(f) -> bool:
    return f.default is not MISSING or f.default_factory is not MISSING
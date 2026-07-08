# types/events/relations.py
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class InReplyTo:
    event_id: str


@dataclass
class RelatesTo:
    in_reply_to: Optional[InReplyTo] = None
    rel_type: Optional[str] = None 
    event_id: Optional[str] = None 

    @classmethod
    def from_dict(cls, data: Optional[dict[str, Any]]) -> Optional["RelatesTo"]:
        if not data:
            return None

        in_reply_to_data = data.get("m.in_reply_to")
        in_reply_to = InReplyTo(**in_reply_to_data) if in_reply_to_data else None

        return cls(
            in_reply_to=in_reply_to,
            rel_type=data.get("rel_type"),
            event_id=data.get("event_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.in_reply_to:
            result["m.in_reply_to"] = {"event_id": self.in_reply_to.event_id}
        if self.rel_type:
            result["rel_type"] = self.rel_type
        if self.event_id:
            result["event_id"] = self.event_id
        return result


@dataclass
class Mentions:
    user_ids: list[str] = field(default_factory=list)
    room: bool = False

    @classmethod
    def from_dict(cls, data: Optional[dict[str, Any]]) -> Optional["Mentions"]:
        if not data:
            return None
        return cls(user_ids=data.get("user_ids", []), room=data.get("room", False))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"user_ids": self.user_ids}
        if self.room:
            result["room"] = True
        return result
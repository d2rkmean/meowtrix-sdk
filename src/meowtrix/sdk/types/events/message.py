from dataclasses import dataclass, field
from typing import Any, ClassVar

from .base_event import BaseContent, BaseEvent


@dataclass
class ImageInfo:
    mimetype: str | None = None
    size: int | None = None
    w: int | None = None
    h: int | None = None
    thumbnail_url: str | None = None
    thumbnail_info: dict[str, Any] | None = None


@dataclass
class FileInfo:
    mimetype: str | None = None
    size: int | None = None
    thumbnail_url: str | None = None
    thumbnail_info: dict[str, Any] | None = None


@dataclass
class AudioInfo:
    mimetype: str | None = None
    size: int | None = None
    duration: int | None = None


@dataclass
class VideoInfo:
    mimetype: str | None = None
    size: int | None = None
    w: int | None = None
    h: int | None = None
    duration: int | None = None
    thumbnail_url: str | None = None
    thumbnail_info: dict[str, Any] | None = None


@dataclass
class TextContent(BaseContent):
    body: str = ""
    msgtype: str = "m.text"
    format: str | None = None
    formatted_body: str | None = None


@dataclass(kw_only=True)
class TextMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.text"

    event_type: str = "m.room.message"
    content: TextContent = field(default_factory=TextContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == TextMessage.MSGTYPE
        )


@dataclass
class EmoteContent(BaseContent):
    body: str = ""
    msgtype: str = "m.emote"
    format: str | None = None
    formatted_body: str | None = None


@dataclass(kw_only=True)
class EmoteMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.emote"

    event_type: str = "m.room.message"
    content: EmoteContent = field(default_factory=EmoteContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == EmoteMessage.MSGTYPE
        )


@dataclass
class NoticeContent(BaseContent):
    body: str = ""
    msgtype: str = "m.notice"
    format: str | None = None
    formatted_body: str | None = None


@dataclass(kw_only=True)
class NoticeMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.notice"

    event_type: str = "m.room.message"
    content: NoticeContent = field(default_factory=NoticeContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == NoticeMessage.MSGTYPE
        )


# ---------- m.image ----------


@dataclass
class ImageContent(BaseContent):
    body: str = ""
    url: str | None = None
    file: dict[str, Any] | None = None
    info: ImageInfo | None = None


@dataclass(kw_only=True)
class ImageMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.image"

    event_type: str = "m.room.message"
    content: ImageContent = field(default_factory=ImageContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == ImageMessage.MSGTYPE
        )


@dataclass
class FileContent(BaseContent):
    body: str = ""
    msgtype: str = "m.file"
    filename: str | None = None
    url: str | None = None
    file: dict[str, Any] | None = None
    info: FileInfo | None = None


@dataclass(kw_only=True)
class FileMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.file"

    event_type: str = "m.room.message"
    content: FileContent = field(default_factory=FileContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == FileMessage.MSGTYPE
        )


@dataclass
class AudioContent(BaseContent):
    body: str = ""
    msgtype: str = "m.audio"
    url: str | None = None
    file: dict[str, Any] | None = None
    info: AudioInfo | None = None


@dataclass(kw_only=True)
class AudioMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.audio"

    event_type: str = "m.room.message"
    content: AudioContent = field(default_factory=AudioContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == AudioMessage.MSGTYPE
        )


@dataclass
class VideoContent(BaseContent):
    body: str = ""
    msgtype: str = "m.video"
    url: str | None = None
    file: dict[str, Any] | None = None
    info: VideoInfo | None = None


@dataclass(kw_only=True)
class VideoMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.video"

    event_type: str = "m.room.message"
    content: VideoContent = field(default_factory=lambda: VideoContent(msgtype="m.video"))

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == VideoMessage.MSGTYPE
        )


@dataclass
class LocationContent(BaseContent):
    body: str = ""
    msgtype: str = "m.location"
    geo_uri: str | None = None
    info: dict[str, Any] | None = None


@dataclass(kw_only=True)
class LocationMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.location"

    event_type: str = "m.room.message"
    content: LocationContent = field(default_factory=LocationContent)

    @staticmethod
    def filter(data: dict[str, Any]) -> bool:
        return (
            data.get("type") == "m.room.message"
            and data.get("content", {}).get("msgtype") == LocationMessage.MSGTYPE
        )

from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional

from .base_event import BaseEvent, BaseContent



@dataclass
class ImageInfo:
    mimetype: Optional[str] = None
    size: Optional[int] = None
    w: Optional[int] = None
    h: Optional[int] = None
    thumbnail_url: Optional[str] = None
    thumbnail_info: Optional[dict[str, Any]] = None


@dataclass
class FileInfo:
    mimetype: Optional[str] = None
    size: Optional[int] = None
    thumbnail_url: Optional[str] = None
    thumbnail_info: Optional[dict[str, Any]] = None


@dataclass
class AudioInfo:
    mimetype: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[int] = None  


@dataclass
class VideoInfo:
    mimetype: Optional[str] = None
    size: Optional[int] = None
    w: Optional[int] = None
    h: Optional[int] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    thumbnail_info: Optional[dict[str, Any]] = None


@dataclass
class TextContent(BaseContent):
    body: str = ""
    msgtype: str = "m.text"
    format: Optional[str] = None
    formatted_body: Optional[str] = None


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
    format: Optional[str] = None
    formatted_body: Optional[str] = None


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
    format: Optional[str] = None
    formatted_body: Optional[str] = None


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
    url: Optional[str] = None 
    file: Optional[dict[str, Any]] = None 
    info: Optional[ImageInfo] = None


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
    filename: Optional[str] = None
    url: Optional[str] = None
    file: Optional[dict[str, Any]] = None
    info: Optional[FileInfo] = None


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
    url: Optional[str] = None
    file: Optional[dict[str, Any]] = None
    info: Optional[AudioInfo] = None


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
    url: Optional[str] = None
    file: Optional[dict[str, Any]] = None
    info: Optional[VideoInfo] = None


@dataclass(kw_only=True)
class VideoMessage(BaseEvent):
    MSGTYPE: ClassVar[str] = "m.video"

    event_type: str = "m.room.message"
    content: VideoContent = field(
        default_factory=lambda: VideoContent(msgtype="m.video")
    )

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
    geo_uri: Optional[str] = None 
    info: Optional[dict[str, Any]] = None


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
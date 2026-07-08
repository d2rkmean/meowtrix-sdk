import uuid
from typing import Any

from httpx import AsyncClient

from .types.events import BaseEvent
from .utils.connection import EndpointType, RequestType, request
from .utils.storage import SQLiteStorage


class Bot:
    def __init__(
        self,
        name: str,
        homeserver: str | None = None,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        filename: str | None = None,
    ) -> None:
        self.name = name
        self.username = username
        self.password = password
        self.access_token = access_token
        self.homeserver = homeserver
        self.filename = filename or f"{name}.session"
        self.device_id: str | None = None
        self.client: AsyncClient = AsyncClient()
        self.storage: SQLiteStorage = SQLiteStorage(self.filename)

        self._next_batch: str | None = None
        self._running: bool = False
        self._txn_counter: int = 0

    async def start(self) -> None:
        await self.storage.connect()

        if not self.homeserver:
            self.homeserver = await self.storage.get("home_server")
        if not self.homeserver:
            raise ValueError("Homeserver not set and not found in storage")

        if not self.access_token:
            self.access_token = await self.storage.get("access_token")

        if (not (self.username and self.password)) and (not self.access_token):
            raise ValueError(
                "Authentication details are required. "
                "Enter your username and password, or enter an access token."
            )

        if not self.access_token and self.username and self.password:
            await self.login()

        self.device_id = self.device_id or await self.storage.get("device_id")
        self._next_batch = await self.storage.get("next_batch")

    async def send_request(
        self,
        endpoint: EndpointType,
        path_params: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        request_data: dict[str, Any] | None = None,
        request_type: RequestType = RequestType.GET,
    ) -> dict[str, Any]:
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        if self.homeserver is None:
            raise ValueError("Homeserver not set")

        output: dict[str, Any] = await request(
            client=self.client,
            server=self.homeserver,
            endpoint=endpoint,
            path_params=path_params,
            params=params,
            json=request_data,
            headers=headers,
            request_type=request_type,
        )
        return output

    async def login(self) -> None:
        if not self.username or not self.password:
            return

        request_data: dict[str, Any] = {
            "type": "m.login.password",
            "identifier": {"type": "m.id.user", "user": self.username},
            "refresh_token": False,
            "password": self.password,
        }

        data: dict[str, Any] = await self.send_request(
            EndpointType.LOGIN, request_data=request_data, request_type=RequestType.POST
        )

        self.access_token = data.get("access_token")
        if self.access_token:
            await self.storage.set("access_token", self.access_token)

        device_id = data.get("device_id")
        if device_id:
            self.device_id = device_id
            await self.storage.set("device_id", device_id)

        home_server = data.get("home_server")
        if home_server:
            self.homeserver = home_server
            await self.storage.set("home_server", home_server)

    def _next_txn_id(self) -> str:
        self._txn_counter += 1
        return f"{self.name}-{uuid.uuid4().hex}-{self._txn_counter}"

    async def send_event(self, room_id: str, event: BaseEvent) -> str:
        content = event.to_dict()["content"]
        event_type = event.event_type or "m.room.message"
        txn_id = self._next_txn_id()

        data = await self.send_request(
            EndpointType.SEND,
            path_params={"room_id": room_id, "event_type": event_type, "txn_id": txn_id},
            request_data=content,
            request_type=RequestType.PUT,
        )
        return data["event_id"]

    async def _sync_once(self, timeout: int = 30000) -> dict[str, Any]:
        params: dict[str, Any] = {"timeout": timeout}
        if self._next_batch:
            params["since"] = self._next_batch
        else:
            params["full_state"] = "false"

        return await self.send_request(
            EndpointType.SYNC, params=params, request_type=RequestType.GET
        )

    async def loop(self, timeout: int = 30000):
        self._running = True
        is_first_sync = self._next_batch is None

        while self._running:
            data = await self._sync_once(timeout=timeout)

            self._next_batch = data.get("next_batch")
            if self._next_batch:
                await self.storage.set("next_batch", self._next_batch)

            if is_first_sync:
                is_first_sync = False
                continue

            rooms = data.get("rooms", {}).get("join", {})
            for room_id, room_data in rooms.items():
                timeline = room_data.get("timeline", {}).get("events", [])
                for raw_event in timeline:
                    raw_event.setdefault("room_id", room_id)
                    yield raw_event

    def stop(self) -> None:
        self._running = False

    async def close(self) -> None:
        await self.client.aclose()
        await self.storage.close()

    async def __aenter__(self) -> "Bot":
        await self.start()
        return self

    async def __aexit__(self, *_: Any, **__: Any) -> None:
        await self.close()

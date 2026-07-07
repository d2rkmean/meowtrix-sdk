from typing import Any

from httpx import AsyncClient

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

    async def start(self) -> None:
        await self.storage.connect()

        if not self.homeserver:
            self.homeserver = await self.storage.get("home_server")

        if not self.homeserver:
            raise ValueError("Homeserver variable not set and not found in storage")

        if not self.access_token:
            self.access_token = await self.storage.get("access_token")

        if (not (self.username and self.password)) and (not self.access_token):
            raise ValueError(
                "Authentication details are required. "
                "Enter your username and password, or enter an access token."
            )

        if not self.access_token and self.username and self.password:
            await self.login()

    async def send_request(
        self,
        endpoint: EndpointType,
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

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "Bot":
        await self.start()
        return self

    async def __aexit__(self, *_: Any, **__: Any) -> None:
        await self.close()

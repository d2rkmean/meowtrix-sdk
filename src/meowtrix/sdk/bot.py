from typing import Any

from httpx import AsyncClient

from .utils.connection import EndpointType, RequestType, request


class Bot:
    def __init__(
        self,
        name: str,
        homeserver: str,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        filename: str | None = None,
    ) -> None:
        if (not (username and password)) and (not access_token):
            # TODO: Use the interactive Matrix login form (including via OAuth)
            raise ValueError(
                "Authentication details are required. "
                "Enter your username and password, or enter an access token."
            )

        self.name = name
        self.homeserver = homeserver
        self.username = username
        self.password = password
        self.access_token = access_token
        self.filename = filename or f"{name}.session"
        self.client: AsyncClient = AsyncClient()

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
        if self.username and self.password:
            request_data: dict[str, Any] = {
                "type": "m.login.password",
                "identifier": {"type": "m.id.user", "user": self.username},
                "password": self.password,
            }
            data: dict[str, Any] = await self.send_request(
                EndpointType.LOGIN, request_data=request_data, request_type=RequestType.POST
            )

            print(data)

    async def close(self) -> None:
        await self.client.aclose()

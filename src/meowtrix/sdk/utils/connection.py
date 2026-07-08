import enum
import logging
from typing import Any

import httpx

logger = logging.getLogger("connection")

import enum


class EndpointType(enum.Enum):
    LOGIN = "_matrix/client/v3/login"
    LOGOUT = "_matrix/client/v3/logout"
    LOGOUT_ALL = "_matrix/client/v3/logout/all"
    REGISTER = "_matrix/client/v3/register"
    REFRESH = "_matrix/client/v3/refresh"
    WHOAMI = "_matrix/client/v3/account/whoami"
    SYNC = "_matrix/client/v3/sync"
    SEND = "_matrix/client/v3/rooms/{room_id}/send/{event_type}/{txn_id}"
    EVENT = "_matrix/client/v3/rooms/{room_id}/event/{event_id}"
    STATE = "_matrix/client/v3/rooms/{room_id}/state/{event_type}/{state_key}"
    STATE_NO_KEY = "_matrix/client/v3/rooms/{room_id}/state/{event_type}"
    STATE_ALL = "_matrix/client/v3/rooms/{room_id}/state"
    REDACT = "_matrix/client/v3/rooms/{room_id}/redact/{event_id}/{txn_id}"
    MESSAGES = "_matrix/client/v3/rooms/{room_id}/messages"
    CONTEXT = "_matrix/client/v3/rooms/{room_id}/context/{event_id}"
    RELATIONS = "_matrix/client/v1/rooms/{room_id}/relations/{event_id}"
    CREATE_ROOM = "_matrix/client/v3/createRoom"
    JOIN_ROOM = "_matrix/client/v3/join/{room_id_or_alias}"
    JOINED_ROOMS = "_matrix/client/v3/joined_rooms"
    JOINED_MEMBERS = "_matrix/client/v3/rooms/{room_id}/joined_members"
    LEAVE_ROOM = "_matrix/client/v3/rooms/{room_id}/leave"
    FORGET_ROOM = "_matrix/client/v3/rooms/{room_id}/forget"
    INVITE = "_matrix/client/v3/rooms/{room_id}/invite"
    KICK = "_matrix/client/v3/rooms/{room_id}/kick"
    BAN = "_matrix/client/v3/rooms/{room_id}/ban"
    UNBAN = "_matrix/client/v3/rooms/{room_id}/unban"
    ROOM_ALIAS = "_matrix/client/v3/directory/room/{room_alias}"
    ROOM_VISIBILITY = "_matrix/client/v3/directory/list/room/{room_id}"
    PUBLIC_ROOMS = "_matrix/client/v3/publicRooms"
    UPGRADE_ROOM = "_matrix/client/v3/rooms/{room_id}/upgrade"
    RECEIPT = "_matrix/client/v3/rooms/{room_id}/receipt/{receipt_type}/{event_id}"
    READ_MARKERS = "_matrix/client/v3/rooms/{room_id}/read_markers"
    TYPING = "_matrix/client/v3/rooms/{room_id}/typing/{user_id}"
    PRESENCE = "_matrix/client/v3/presence/{user_id}/status"
    PROFILE = "_matrix/client/v3/profile/{user_id}"
    DISPLAYNAME = "_matrix/client/v3/profile/{user_id}/displayname"
    AVATAR_URL = "_matrix/client/v3/profile/{user_id}/avatar_url"
    DEVICES = "_matrix/client/v3/devices"
    DEVICE = "_matrix/client/v3/devices/{device_id}"
    DELETE_DEVICES = "_matrix/client/v3/delete_devices"
    ACCOUNT_DATA = "_matrix/client/v3/user/{user_id}/account_data/{type}"
    ROOM_ACCOUNT_DATA = "_matrix/client/v3/user/{user_id}/rooms/{room_id}/account_data/{type}"
    KEYS_UPLOAD = "_matrix/client/v3/keys/upload"
    KEYS_QUERY = "_matrix/client/v3/keys/query"
    KEYS_CLAIM = "_matrix/client/v3/keys/claim"
    KEYS_CHANGES = "_matrix/client/v3/keys/changes"
    KEYS_SIGNATURES_UPLOAD = "_matrix/client/v3/keys/signatures/upload"
    SEND_TO_DEVICE = "_matrix/client/v3/sendToDevice/{event_type}/{txn_id}"
    ROOM_KEYS_VERSION = "_matrix/client/v3/room_keys/version"
    ROOM_KEYS = "_matrix/client/v3/room_keys/keys"
    MEDIA_UPLOAD = "_matrix/media/v3/upload"
    MEDIA_DOWNLOAD = "_matrix/media/v3/download/{server_name}/{media_id}"
    MEDIA_THUMBNAIL = "_matrix/media/v3/thumbnail/{server_name}/{media_id}"
    MEDIA_CONFIG = "_matrix/client/v1/media/config"
    PUSHERS = "_matrix/client/v3/pushers"
    PUSHRULES = "_matrix/client/v3/pushrules"
    SEARCH = "_matrix/client/v3/search"
    FILTER = "_matrix/client/v3/user/{user_id}/filter"
    FILTER_BY_ID = "_matrix/client/v3/user/{user_id}/filter/{filter_id}"
    VERSIONS = "_matrix/client/versions"
    CAPABILITIES = "_matrix/client/v3/capabilities"
    WELL_KNOWN_CLIENT = "_matrix/client/well-known"

    def format(self, **kwargs: str) -> str:
        return self.value.format(**kwargs)


class RequestType(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ErrorCode(enum.Enum):
    """https://spec.matrix.org/v1.18/client-server-api/#common-error-codes"""

    M_BAD_JSON = "M_BAD_JSON"
    M_FORBIDDEN = "M_FORBIDDEN"
    M_LIMIT_EXCEEDED = "M_LIMIT_EXCEEDED"
    M_MISSING_TOKEN = "M_MISSING_TOKEN"
    M_NOT_FOUND = "M_NOT_FOUND"
    M_NOT_JSON = "M_NOT_JSON"
    M_RESOURCE_LIMIT_EXCEEDED = "M_RESOURCE_LIMIT_EXCEEDED"
    M_USER_LIMIT_EXCEEDED = "M_USER_LIMIT_EXCEEDED"
    M_UNKNOWN = "M_UNKNOWN"
    M_UNKNOWN_DEVICE = "M_UNKNOWN_DEVICE"
    M_UNKNOWN_TOKEN = "M_UNKNOWN_TOKEN"
    M_UNRECOGNIZED = "M_UNRECOGNIZED"
    M_USER_LOCKED = "M_USER_LOCKED"
    M_USER_SUSPENDED = "M_USER_SUSPENDED"
    M_BAD_STATE = "M_BAD_STATE"
    M_CANNOT_LEAVE_SERVER_NOTICE_ROOM = "M_CANNOT_LEAVE_SERVER_NOTICE_ROOM"
    M_CAPTCHA_INVALID = "M_CAPTCHA_INVALID"
    M_EXCLUSIVE = "M_EXCLUSIVE"
    M_GUEST_ACCESS_FORBIDDEN = "M_GUEST_ACCESS_FORBIDDEN"
    M_INCOMPATIBLE_ROOM_VERSION = "M_INCOMPATIBLE_ROOM_VERSION"
    M_INVALID_PARAM = "M_INVALID_PARAM"
    M_USER_IN_USE = "M_USER_IN_USE"
    M_USER_DEACTIVATED = "M_USER_DEACTIVATED"
    M_UNSUPPORTED_ROOM_VERSION = "M_UNSUPPORTED_ROOM_VERSION"
    M_UNAUTHORIZED = "M_UNAUTHORIZED"
    M_TOO_LARGE = "M_TOO_LARGE"
    M_THREEPID_NOT_FOUND = "M_THREEPID_NOT_FOUND"
    M_THREEPID_MEDIUM_NOT_SUPPORTED = "M_THREEPID_MEDIUM_NOT_SUPPORTED"
    M_THREEPID_IN_USE = "M_THREEPID_IN_USE"
    M_THREEPID_DENIED = "M_THREEPID_DENIED"
    M_THREEPID_AUTH_FAILED = "M_THREEPID_AUTH_FAILED"
    M_SERVER_NOT_TRUSTED = "M_SERVER_NOT_TRUSTED"
    M_ROOM_IN_USE = "M_ROOM_IN_USE"
    M_MISSING_PARAM = "M_MISSING_PARAM"
    M_INVALID_USERNAME = "M_INVALID_USERNAME"
    M_INVALID_ROOM_STATE = "M_INVALID_ROOM_STATE"


class MatrixRequestError(Exception):
    """https://spec.matrix.org/v1.18/client-server-api/#standard-error-response"""

    def __init__(
        self,
        error_code: ErrorCode | str,
        description: str,
        status_code: int = 400,
        **kwargs: dict[str, Any],
    ) -> None:
        self.error_code = error_code
        self.description = description
        self.status_code = status_code
        self.__dict__.update(kwargs)
        code_str = error_code.value if isinstance(error_code, ErrorCode) else error_code

        super().__init__(f"Matrix connection error ({code_str}): {description}")


async def request(
    client: httpx.AsyncClient,
    server: str,
    endpoint: EndpointType,
    path_params: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    request_type: RequestType = RequestType.GET,
    timeout: float | None = None,  # noqa: ASYNC109
) -> dict[str, Any]:
    """Send an HTTP request to a Matrix server and return the parsed JSON response.

    Builds the request URL as ``https://{server}/{endpoint}``, substituting
    any ``{placeholder}`` segments in the endpoint's path template using
    `path_params`, and sends it using the specified HTTP method
    (`request_type`), along with any given query parameters, JSON body,
    headers, and an optional request timeout.

    If the server responds with a status code other than 200, attempts to
    parse the response body as JSON and extract the `errcode` and `error`
    fields to raise a `MatrixRequestError`. If the error response body is
    not valid JSON, or does not contain the expected error fields, a
    `MatrixRequestError` is also raised with an appropriate message.

    Args:
        client: The async HTTP client used to perform the request.
        server: The Matrix server host to send the request to.
        endpoint: The API endpoint, whose path template may contain
            ``{placeholder}`` segments (e.g. ``{room_id}``) to be filled
            in from `path_params`.
        path_params: Values used to fill in ``{placeholder}`` segments in
            the endpoint's path template (e.g. ``room_id``, ``event_id``).
            Defaults to None.
        params: Query parameters to include in the request. Defaults to
            None.
        json: JSON request body. Defaults to None.
        headers: Additional HTTP headers to include in the request.
            Defaults to None.
        request_type: The HTTP method to use for the request (GET, POST,
            etc.). Defaults to `RequestType.GET`.
        timeout: The maximum time (in seconds) to wait for the request
            to complete. Can be a single float or None to inherit the
            client's default timeout configuration. Defaults to None.

    Returns:
        dict: The parsed JSON body of the successful response.

    Raises:
        MatrixRequestError: If the response status code is not 200. The
            error code is taken from the `errcode` field of the response
            body (converted to `ErrorCode` if it's a recognized value,
            otherwise used as-is). Also raised if the error response body
            is not valid JSON or is missing the expected `errcode`/`error`
            fields.
    """
    path = endpoint.format(**path_params) if path_params else endpoint.value
    url = f"https://{server}/{path}"
    logger.debug(f"HTTP request: {url}")

    print(json)
    response = await client.request(
        request_type.value, url, params=params, json=json, headers=headers, timeout=timeout
    )

    if response.status_code != 200:
        try:
            data: dict[str, Any] = response.json()
        except ValueError:
            raise MatrixRequestError(
                ErrorCode.M_UNKNOWN,
                f"Non-JSON error response: {response.text}",
                response.status_code,
            )

        raw_errcode = data.get("errcode")
        error = data.get("error")

        if raw_errcode and error:
            try:
                errcode = ErrorCode(raw_errcode)
            except ValueError:
                errcode = raw_errcode
            raise MatrixRequestError(errcode, error, response.status_code)

        raise MatrixRequestError(
            ErrorCode.M_UNKNOWN, f"Unexpected error response: {data}", response.status_code
        )

    output_json: dict[str, Any] = response.json()
    return output_json
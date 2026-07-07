import enum
import logging
from typing import Any

import httpx

logger = logging.getLogger("connection")


class EndpointType(enum.Enum):
    LOGIN = "_matrix/client/v3/login"
    SYNC = "_matrix/client/v3/sync"

    def format(self, **kwargs: dict[str, str]) -> str:
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
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    request_type: RequestType = RequestType.GET,
    timeout: float | None = None,  # noqa: ASYNC109
) -> dict[str, Any]:
    """Send an HTTP request to a Matrix server and return the parsed JSON response.

    Builds the request URL as ``https://{server}/{endpoint}`` and sends it
    using the specified HTTP method (`request_type`), along with any given
    query parameters, JSON body, headers, and an optional request timeout.
    If the server responds with a status code other than 200, attempts to
    parse the response body as JSON and extract the `errcode` and `error`
    fields to raise a `MatrixRequestError`. If the error response body is
    not valid JSON, or does not contain the expected error fields, a
    `MatrixRequestError` is also raised with an appropriate message.

    Args:
        client: The async HTTP client used to perform the request.
        server: The Matrix server host to send the request to.
        endpoint: The API endpoint path (without a leading slash), appended
            to the server address.
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
            fields."""

    url = f"https://{server}/{endpoint.value}"
    logger.debug(f"HTTP request: {url}")

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

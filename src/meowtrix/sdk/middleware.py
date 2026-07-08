from typing import Awaitable, Callable

from .types.events import BaseEvent

NextMiddleware = Callable[[BaseEvent], Awaitable[None]]


class Middleware:
    async def __call__(self, event: BaseEvent, call_next: NextMiddleware) -> None:
        await call_next(event)


class IgnoreSelfMiddleware(Middleware):
    async def __call__(self, event: BaseEvent, call_next: NextMiddleware) -> None:
        bot_user_id = getattr(event.bot, "username", None)
        if bot_user_id and event.sender_id == bot_user_id:
            return
        await call_next(event)
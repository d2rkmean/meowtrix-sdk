import asyncio
from collections.abc import Callable
from logging import getLogger
from typing import Any

from .bot import Bot
from .filters import FilterLike
from .middleware import Middleware
from .router import Handler, Router
from .types.events import BaseEvent

logger = getLogger("listener")


class Listener:
    def __init__(self, bot: Bot | None = None) -> None:
        self.bots: list[Bot] = []
        self._root_router = Router(name="root")
        self._running = False
        self._registered_events: set[type[BaseEvent]] = set()
        self._tasks: list[asyncio.Task] = []

        if bot is not None:
            self.add_bot(bot)

    def add_bot(self, bot: Bot) -> None:
        if bot in self.bots:
            raise ValueError(f"Bot {bot.name!r} is already added to this Listener")
        self.bots.append(bot)

    def register_event(self, event_cls: type[BaseEvent]) -> None:
        if not issubclass(event_cls, BaseEvent):
            raise TypeError(f"{event_cls!r} must be a subclass of BaseEvent")

        if "filter" not in event_cls.__dict__:
            raise TypeError(
                f"{event_cls!r} does not override filter() — "
                f"BaseEvent.from_dict will not be able to recognize it"
            )

        self._registered_events.add(event_cls)

    def include(self, router: Router) -> None:
        self._root_router.include(router)

    def middleware(self, mw: Middleware) -> None:
        self._root_router.middleware(mw)

    def on(self, event_cls: type[BaseEvent], *filters: FilterLike) -> Callable[[Handler], Handler]:
        self.register_event(event_cls)
        return self._root_router.on(event_cls, *filters)

    async def _handle_raw(self, raw_event: dict[str, Any], bot: Bot) -> None:
        logger.debug("RAW EVENT: %r", raw_event)  # добавить временно
        try:
            event = BaseEvent.from_dict(raw_event, bot=bot)
        except ValueError as exc:
            logger.debug("Event not matched by any registered class: %s", exc)  # было — тихо return
            return
        logger.debug("Parsed event: %r", event)
        await self._root_router.dispatch(event)

    async def _run_bot(self, bot: Bot, timeout: int) -> None:
        async for raw_event in bot.loop(timeout=timeout):
            if not self._running:
                break
            await self._handle_raw(raw_event, bot)

    async def run(self, timeout: int = 30000) -> None:
        if not self.bots:
            raise ValueError("No bots added. Use add_bot() or pass a bot to the constructor.")

        self._running = True

        self._tasks = [
            asyncio.create_task(self._run_bot(bot, timeout), name=f"listener-{bot.name}")
            for bot in self.bots
        ]

        try:
            results = await asyncio.gather(*self._tasks, return_exceptions=True)
            for bot, result in zip(self.bots, results):
                if isinstance(result, Exception):
                    print(f"[Listener] Bot {bot.name!r} exited with error: {result!r}")
        finally:
            self._running = False

    def stop(self) -> None:
        self._running = False
        for bot in self.bots:
            bot.stop()
        for task in self._tasks:
            if not task.done():
                task.cancel()

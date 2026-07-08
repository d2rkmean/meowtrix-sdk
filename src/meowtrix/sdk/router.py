import asyncio
from collections.abc import Awaitable, Callable

from .filters import FilterLike, apply_filters
from .middleware import Middleware, NextMiddleware
from .types.events import BaseEvent

Handler = Callable[[BaseEvent], Awaitable[None]]


class Router:
    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__
        self._handlers: dict[type[BaseEvent], list[tuple[Handler, list[FilterLike]]]] = {}
        self._sub_routers: list[Router] = []
        self._middlewares: list[Middleware] = []

    def on(self, event_cls: type[BaseEvent], *filters: FilterLike) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self._handlers.setdefault(event_cls, []).append((func, list(filters)))
            return func

        return decorator

    def add_handler(
        self, event_cls: type[BaseEvent], handler: Handler, *filters: FilterLike
    ) -> None:
        self._handlers.setdefault(event_cls, []).append((handler, list(filters)))

    def middleware(self, mw: Middleware) -> None:
        self._middlewares.append(mw)

    def include(self, router: "Router") -> None:
        self._sub_routers.append(router)

    def _collect_handlers(self, event: BaseEvent) -> list[Handler]:
        matched: list[Handler] = []
        for handler, filters in self._handlers.get(type(event), []):
            if apply_filters(event, filters):
                matched.append(handler)

        for sub in self._sub_routers:
            matched.extend(sub._collect_handlers(event))

        return matched

    def _collect_middlewares(self) -> list[Middleware]:
        middlewares = list(self._middlewares)
        for sub in self._sub_routers:
            middlewares.extend(sub._collect_middlewares())
        return middlewares

    async def dispatch(self, event: BaseEvent) -> None:
        handlers = self._collect_handlers(event)
        if not handlers:
            return

        middlewares = self._collect_middlewares()

        async def run_handlers(ev: BaseEvent) -> None:
            results = await asyncio.gather(
                *(handler(ev) for handler in handlers),
                return_exceptions=True,
            )
            for result in results:
                if isinstance(result, Exception):
                    print(f"[{self.name}] Handler error: {result!r}")

        chain: NextMiddleware = run_handlers
        for mw in reversed(middlewares):
            chain = self._wrap(mw, chain)

        await chain(event)

    @staticmethod
    def _wrap(mw: Middleware, next_call: NextMiddleware) -> NextMiddleware:
        async def wrapped(ev: BaseEvent) -> None:
            await mw(ev, next_call)

        return wrapped

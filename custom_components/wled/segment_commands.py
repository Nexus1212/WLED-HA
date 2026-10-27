"""Delayed segment commands, independent of the Home Assistant platform lock."""

import asyncio
from asyncio import sleep
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

TURN_ON_DELAY_SECONDS = 1.0
EVENT_SEGMENT_TURN_ON_REQUESTED = "wled_segment_turn_on_requested"

ALLOWED_EFFECTS = (
    "Solid", "Bends", "Candle Multi", "Lake", "Sine", "Twinklefox", "Twinkleup",
    "BPM", "Chase 2", "Chunchun", "Heartbeat", "PS Chase", "Chase", "Loading",
    "Scan", "Scan Dual", "Two Dots", "Fireworks 1D", "Meteor", "PS Fire 1D",
    "PS Fireworks 1D", "Flow Stripe", "Glitter", "Palette", "Rainbow",
    "PS Sonic Boom", "PS Sonic Stream", "PS Starburst", "Sunrise",
)


def filtered_effects(available: set[str]) -> list[str]:
    """Keep firmware names intact and use the configured display order."""
    return [name for name in ALLOWED_EFFECTS if name in available]


class SegmentCommands:
    """Coalesce ON requests during a fixed delay; OFF cancels pending ON.

    Service calls return after scheduling, so the platform's semaphore never
    blocks OFF or other segments for the duration of the delay. Actual commands
    for this segment are serialized. No relay acknowledgement is consulted.
    """

    def __init__(
        self,
        send_on: Callable[..., Awaitable[None]],
        send_off: Callable[..., Awaitable[None]],
        emit_request: Callable[[], None],
        create_task: Callable[[Coroutine[Any, Any, None]], asyncio.Task[None]],
    ) -> None:
        self._send_on = send_on
        self._send_off = send_off
        self._emit_request = emit_request
        self._create_task = create_task
        self._lock = asyncio.Lock()
        self._pending: dict[str, Any] | None = None
        self._timer_task: asyncio.Task[None] | None = None
        self._tasks: set[asyncio.Task[None]] = set()
        self._closed = False

    async def turn_on(self, is_on: bool, **kwargs: Any) -> None:
        """Delay an OFF-to-ON request, but not changes to a running segment."""
        if self._closed:
            return
        if self._pending is not None:
            self._pending.update(kwargs)
            return
        if is_on:
            async with self._lock:
                if not self._closed:
                    await self._send_on(**kwargs)
            return

        self._pending = dict(kwargs)
        self._emit_request()
        task = self._create_task(self._delayed_on())
        self._timer_task = task
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _delayed_on(self) -> None:
        await sleep(TURN_ON_DELAY_SECONDS)
        async with self._lock:
            if self._closed or self._pending is None:
                return
            kwargs = self._pending
            self._pending = None
            self._timer_task = None
            await self._send_on(**kwargs)

    def cancel_pending(self) -> None:
        """Cancel only a waiting command, never an HTTP command in flight."""
        self._pending = None
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None

    async def turn_off(self, **kwargs: Any) -> None:
        """Cancel the countdown and serialize OFF after any in-flight ON."""
        self.cancel_pending()
        async with self._lock:
            if not self._closed:
                await self._send_off(**kwargs)

    async def close(self) -> None:
        """Remove waiting/running jobs when the entity is unloaded."""
        self._closed = True
        self.cancel_pending()
        tasks = tuple(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

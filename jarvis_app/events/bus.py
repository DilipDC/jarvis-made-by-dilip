from __future__ import annotations
import asyncio
import threading
from collections import defaultdict
from typing import Any, Callable

class EventBus:
    def __init__(self) -> None:
        self._sync: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self._async: dict[str, list[Callable[[dict[str, Any]], Any]]] = defaultdict(list)
        self._lock = threading.RLock()

    def on(self, event: str, callback: Callable[[dict[str, Any]], Any]) -> None:
        with self._lock:
            if asyncio.iscoroutinefunction(callback):
                self._async[event].append(callback)
            else:
                self._sync[event].append(callback)

    def emit(self, event: str, **payload: Any) -> dict[str, Any]:
        data = {"event": event, **payload}
        with self._lock:
            callbacks = list(self._sync.get(event, ()))
        for callback in callbacks:
            try:
                callback(data)
            except Exception:
                pass
        return data

    async def aemit(self, event: str, **payload: Any) -> dict[str, Any]:
        data = self.emit(event, **payload)
        with self._lock:
            callbacks = list(self._async.get(event, ()))
        for callback in callbacks:
            try:
                await callback(data)
            except Exception:
                pass
        return data

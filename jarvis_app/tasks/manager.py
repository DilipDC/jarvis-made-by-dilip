from __future__ import annotations
import threading, time, uuid
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class TaskRecord:
    task_id: str
    name: str
    state: str
    created_at: float
    started_at: float | None = None
    ended_at: float | None = None
    progress: float = 0.0
    detail: str = ""
    error: str | None = None

class TaskManager:
    STATES = {"CREATED", "PLANNING", "WAITING_CONFIRMATION", "EXECUTING", "OBSERVING", "VERIFYING", "COMPLETED", "FAILED", "CANCELLED"}
    def __init__(self, store, events) -> None:
        self.store = store
        self.events = events
        self._items: dict[str, TaskRecord] = {}
        self._lock = threading.RLock()

    def create(self, name: str) -> TaskRecord:
        t = TaskRecord(str(uuid.uuid4()), name, "CREATED", time.time())
        with self._lock:
            self._items[t.task_id] = t
        self._save(t)
        self.events.emit("task.created", task=asdict(t))
        return t

    def update(self, task_id: str, state: str | None = None, progress: float | None = None, detail: str | None = None, error: str | None = None) -> TaskRecord:
        if state is not None and state not in self.STATES:
            raise ValueError(f"invalid task state: {state}")
        with self._lock:
            t = self._items[task_id]
            if state is not None:
                if t.started_at is None and state in {"PLANNING", "EXECUTING", "OBSERVING", "VERIFYING"}:
                    t.started_at = time.time()
                if state in {"COMPLETED", "FAILED", "CANCELLED"}:
                    t.ended_at = time.time()
                t.state = state
            if progress is not None:
                t.progress = max(0.0, min(1.0, progress))
            if detail is not None:
                t.detail = detail
            if error is not None:
                t.error = error
            self._save(t)
            data = asdict(t)
        self.events.emit("task.updated", task=data)
        return t

    def _save(self, t: TaskRecord) -> None:
        self.store.save_task(t.task_id, t.name, t.state, t.created_at, t.started_at, t.ended_at, t.progress, t.detail, t.error)

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return [asdict(v) for v in sorted(self._items.values(), key=lambda x: x.created_at, reverse=True)]

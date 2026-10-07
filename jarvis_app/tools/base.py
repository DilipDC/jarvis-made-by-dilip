from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class ToolSpec:
    name: str
    description: str
    permission: str = "SAFE"
    platform: str = "all"
    source: str = "builtin"
    latency: str = "fast"
    handler: Callable[..., Any] | None = None

    def schema(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "permission": self.permission, "platform": self.platform, "source": self.source, "latency": self.latency}

@dataclass
class ToolRegistry:
    tools: dict[str, ToolSpec] = field(default_factory=dict)
    def register(self, spec: ToolSpec) -> None: self.tools[spec.name] = spec
    def get(self, name: str) -> ToolSpec | None: return self.tools.get(name)
    def describe(self) -> list[dict[str, Any]]: return [t.schema() for t in self.tools.values()]
    def call(self, name: str, **kwargs: Any) -> Any:
        tool = self.get(name)
        if not tool or not tool.handler:
            raise KeyError(f"Unknown tool: {name}")
        return tool.handler(**kwargs)

from __future__ import annotations
import importlib.util
from pathlib import Path
import json

class MCPManager:
    """Lazy MCP client. Servers are subprocesses and are started only when inspected/called."""
    def __init__(self, config_path=None):
        self.servers={}
        self.sdk_available=bool(importlib.util.find_spec("mcp"))
        self.config_path=Path(config_path) if config_path else None
        self._load_defaults()

    def _load_defaults(self):
        self.register("filesystem", {
            "enabled": True,
            "transport": "stdio",
            "trust": "CONFIRM",
            "command": "npx",
            "windows_command": "cmd",
            "args": ["-y","@modelcontextprotocol/server-filesystem","."],
            "windows_args": ["/c","npx","-y","@modelcontextprotocol/server-filesystem","."],
            "description": "Official MCP filesystem server, restricted to the JARVIS working directory."
        })
        self.register("memory", {
            "enabled": True,
            "transport": "stdio",
            "trust": "SAFE",
            "command": "npx",
            "windows_command": "cmd",
            "args": ["-y","@modelcontextprotocol/server-memory"],
            "windows_args": ["/c","npx","-y","@modelcontextprotocol/server-memory"],
            "description": "Official MCP knowledge-graph memory server."
        })

    def register(self,name,config):
        self.servers[name]={
            "name":name,
            "config":config,
            "enabled":bool(config.get("enabled",True)),
            "trust":config.get("trust","CONFIRM"),
            "status":"CONFIGURED"
        }

    def unregister(self,name): self.servers.pop(name,None)

    def health(self):
        return {
            "available":self.sdk_available,
            "sdk_available":self.sdk_available,
            "count":len(self.servers),
            "servers":[
                {"name":v["name"],"enabled":v["enabled"],"trust":v["trust"],"status":v["status"],
                 "transport":v["config"].get("transport","stdio"),"description":v["config"].get("description","")}
                for v in self.servers.values()
            ]
        }

    def _params(self,server):
        from mcp import StdioServerParameters
        cfg=server["config"]
        import os
        if os.name=="nt":
            return StdioServerParameters(command=cfg.get("windows_command",cfg["command"]),args=cfg.get("windows_args",cfg.get("args",[])))
        return StdioServerParameters(command=cfg["command"],args=cfg.get("args",[]))

    async def inspect(self,name):
        if name not in self.servers: raise KeyError(name)
        server=self.servers[name]
        if not server["enabled"]: return {"name":name,"enabled":False,"tools":[]}
        if not self.sdk_available: return {"name":name,"status":"BLOCKED","reason":"Install the optional mcp dependency."}
        from mcp import Client
        try:
            async with Client(self._params(server)) as client:
                tools=await client.list_tools()
                server["status"]="ONLINE"
                return {"name":name,"status":"ONLINE","tools":[
                    {"name":getattr(t,"name",""),"description":getattr(t,"description","")}
                    for t in getattr(tools,"tools",[])
                ]}
        except Exception as exc:
            server["status"]="ERROR"
            return {"name":name,"status":"ERROR","error":str(exc)}

    async def call(self,name,tool_name,arguments=None):
        server=self.servers[name]
        if server["trust"]=="BLOCKED": raise PermissionError("MCP server blocked by trust policy")
        if not self.sdk_available: raise RuntimeError("MCP SDK not installed")
        from mcp import Client
        async with Client(self._params(server)) as client:
            result=await client.call_tool(tool_name, arguments or {})
            server["status"]="ONLINE"
            return result

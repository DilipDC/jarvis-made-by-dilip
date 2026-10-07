from __future__ import annotations
import importlib.util, asyncio

class MCPManager:
    def __init__(self): self.servers={}; self.sdk_available=bool(importlib.util.find_spec('mcp'))
    def register(self,name,config): self.servers[name]={'name':name,'config':config,'enabled':bool(config.get('enabled',True)),'trust':config.get('trust','CONFIRM'),'status':'CONFIGURED'}
    def unregister(self,name): self.servers.pop(name,None)
    def health(self): return {'available':self.sdk_available,'sdk_available':self.sdk_available,'servers':list(self.servers.values())}
    async def inspect(self,name):
        server=self.servers[name]
        if not server['enabled']: return {'name':name,'enabled':False,'tools':[]}
        if not self.sdk_available: return {'name':name,'enabled':True,'status':'BLOCKED','reason':'install optional mcp dependency'}
        from mcp import Client  # type: ignore
        endpoint=server['config'].get('url')
        if not endpoint: return {'name':name,'status':'INVALID','reason':'missing url'}
        async with Client(endpoint) as client:
            tools=await client.list_tools()
            return {'name':name,'status':'ONLINE','tools':[getattr(t,'name',str(t)) for t in getattr(tools,'tools',[])]}
    async def call(self,name,tool_name,arguments=None):
        server=self.servers[name]
        if server['trust']=='BLOCKED': raise PermissionError('MCP server blocked by trust policy')
        if not self.sdk_available: raise RuntimeError('MCP SDK not installed; install optional mcp package')
        from mcp import Client  # type: ignore
        endpoint=server['config']['url']
        async with Client(endpoint) as client:
            return await client.call_tool(tool_name, arguments or {})

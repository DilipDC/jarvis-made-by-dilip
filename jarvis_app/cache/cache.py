from __future__ import annotations
import hashlib, json, sqlite3, threading, time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class CacheRecord:
    key: str
    value: Any
    created_at: float
    last_accessed: float
    expires_at: float | None
    source: str = ""
    importance: int = 1
    version: str = "1"

class TempCache:
    def __init__(self,max_entries=128,max_bytes=4*1024*1024):
        self.max_entries=max(8,max_entries); self.max_bytes=max(64*1024,max_bytes)
        self._items=OrderedDict(); self._bytes=0; self._lock=threading.RLock()
    @staticmethod
    def _size(v):
        try:return len(json.dumps(v,ensure_ascii=False,default=str).encode())
        except Exception:return len(repr(v).encode())
    def get(self,key):
        now=time.time()
        with self._lock:
            r=self._items.get(key)
            if r is None:return None
            if r.expires_at is not None and r.expires_at<=now:self._delete_unlocked(key); return None
            r.last_accessed=now; self._items.move_to_end(key); return r.value
    def set(self,key,value,ttl=None,source="",importance=1):
        now=time.time(); r=CacheRecord(key,value,now,now,now+ttl if ttl else None,source,importance)
        with self._lock:
            self._delete_unlocked(key); self._items[key]=r; self._bytes+=self._size(value); self._trim_unlocked()
    def delete(self,key):
        with self._lock:return self._delete_unlocked(key)
    def _delete_unlocked(self,key):
        old=self._items.pop(key,None)
        if old is None:return False
        self._bytes-=self._size(old.value); return True
    def clear(self):
        with self._lock:self._items.clear(); self._bytes=0
    def _trim_unlocked(self):
        while len(self._items)>self.max_entries or self._bytes>self.max_bytes:
            self._items.popitem(last=False); self._bytes=sum(self._size(v.value) for v in self._items.values())
    def stats(self):
        with self._lock:return {"kind":"temp","entries":len(self._items),"bytes":self._bytes,"max_entries":self.max_entries,"max_bytes":self.max_bytes}

class PersistentCache:
    def __init__(self,directory,max_bytes=16*1024*1024):
        self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True); self.path=self.directory/"persistent.sqlite3"
        self.max_bytes=max(256*1024,max_bytes); self._lock=threading.RLock(); self._init()
    def _connect(self):
        c=sqlite3.connect(self.path,timeout=10); c.row_factory=sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=NORMAL"); return c
    def _init(self):
        with self._connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY,value TEXT NOT NULL,created_at REAL NOT NULL,last_accessed REAL NOT NULL,expires_at REAL,source TEXT NOT NULL,importance INTEGER NOT NULL,version TEXT NOT NULL,size_bytes INTEGER NOT NULL)""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_cache_lru ON cache(last_accessed)")
    def get(self,key):
        now=time.time()
        with self._lock,self._connect() as c:
            r=c.execute("SELECT * FROM cache WHERE key=?",(key,)).fetchone()
            if r is None:return None
            if r["expires_at"] is not None and r["expires_at"]<=now:c.execute("DELETE FROM cache WHERE key=?",(key,)); return None
            c.execute("UPDATE cache SET last_accessed=? WHERE key=?",(now,key))
            try:return json.loads(r["value"])
            except Exception:return None
    def set(self,key,value,ttl=None,source="",importance=1):
        now=time.time(); payload=json.dumps(value,ensure_ascii=False,default=str,separators=(",",":")); size=len(payload.encode())
        with self._lock,self._connect() as c:
            c.execute("""INSERT INTO cache(key,value,created_at,last_accessed,expires_at,source,importance,version,size_bytes)
VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,last_accessed=excluded.last_accessed,expires_at=excluded.expires_at,source=excluded.source,importance=excluded.importance,version=excluded.version,size_bytes=excluded.size_bytes""",
                      (key,payload,now,now,now+ttl if ttl else None,source,importance,"1",size))
            self._compact_unlocked(c)
    def delete(self,key):
        with self._lock,self._connect() as c:return c.execute("DELETE FROM cache WHERE key=?",(key,)).rowcount>0
    def clear(self):
        with self._lock,self._connect() as c:c.execute("DELETE FROM cache")
    def _compact_unlocked(self,c):
        c.execute("DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at<=?",(time.time(),))
        total=c.execute("SELECT COALESCE(SUM(size_bytes),0) total FROM cache").fetchone()["total"]
        while total>self.max_bytes:
            r=c.execute("SELECT key,size_bytes FROM cache ORDER BY importance ASC,last_accessed ASC LIMIT 1").fetchone()
            if r is None:break
            c.execute("DELETE FROM cache WHERE key=?",(r["key"],)); total-=r["size_bytes"]
    def compact(self):
        with self._lock,self._connect() as c:self._compact_unlocked(c)
    def stats(self):
        with self._lock,self._connect() as c:
            r=c.execute("SELECT COUNT(*) entries,COALESCE(SUM(size_bytes),0) bytes FROM cache").fetchone()
            return {"kind":"persistent","entries":r["entries"],"bytes":r["bytes"],"max_bytes":self.max_bytes,"path":str(self.path)}

class CacheManager:
    def __init__(self,temp_max_entries=128,temp_max_bytes=4*1024*1024,persistent_max_bytes=16*1024*1024,root="data/cache",max_entries=None,max_bytes=None):
        # max_entries/max_bytes are retained as compatibility aliases for the public API.
        if max_entries is not None: temp_max_entries=max_entries
        if max_bytes is not None: temp_max_bytes=max_bytes
        root=Path(root); self.temp=TempCache(temp_max_entries,temp_max_bytes); self.persistent=PersistentCache(root/"persistent",persistent_max_bytes); (root/"temp").mkdir(parents=True,exist_ok=True)
    @staticmethod
    def key(namespace,*parts):
        return hashlib.sha256("\x1f".join([namespace,*(str(p) for p in parts)]).encode()).hexdigest()
    def get(self,key,persistent=False):return (self.persistent if persistent else self.temp).get(key)
    def set(self,key,value,ttl=None,source="",persistent=False,importance=1):(self.persistent if persistent else self.temp).set(key,value,ttl,source,importance)
    def delete(self,key,persistent=False):return (self.persistent if persistent else self.temp).delete(key)
    def clear_temp(self):self.temp.clear()
    def compact_persistent(self):self.persistent.compact()
    def stats(self):return {"temp":self.temp.stats(),"persistent":self.persistent.stats()}

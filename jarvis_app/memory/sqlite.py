from __future__ import annotations
import sqlite3, threading, time, json
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, kind TEXT NOT NULL, importance INTEGER DEFAULT 1, tags TEXT DEFAULT '', created_at REAL NOT NULL, updated_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind);
CREATE INDEX IF NOT EXISTS idx_memories_time ON memories(updated_at);
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(content, tags, content='memories', content_rowid='id');
CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, summary TEXT, updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS tool_runs(id INTEGER PRIMARY KEY AUTOINCREMENT, tool TEXT, state TEXT, latency_ms REAL, result TEXT, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS python_tasks(task_id TEXT PRIMARY KEY, script TEXT, pid INTEGER, status TEXT, started_at REAL, ended_at REAL, stdout TEXT, stderr TEXT, exit_code INTEGER, working_directory TEXT);
CREATE TABLE IF NOT EXISTS tasks(task_id TEXT PRIMARY KEY, name TEXT NOT NULL, state TEXT NOT NULL, created_at REAL NOT NULL, started_at REAL, ended_at REAL, progress REAL DEFAULT 0, detail TEXT DEFAULT '', error TEXT);
CREATE TABLE IF NOT EXISTS scheduled_tasks(id TEXT PRIMARY KEY, task_json TEXT NOT NULL, updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT UNIQUE, title TEXT, metadata TEXT, created_at REAL NOT NULL, updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS document_chunks(id INTEGER PRIMARY KEY AUTOINCREMENT, document_id INTEGER NOT NULL, chunk_index INTEGER NOT NULL, content TEXT NOT NULL, metadata TEXT, FOREIGN KEY(document_id) REFERENCES documents(id));
CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(content, chunk_id UNINDEXED);
CREATE TABLE IF NOT EXISTS audit_events(id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, permission TEXT, detail TEXT, created_at REAL NOT NULL);
'''

class MemoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True); self._lock = threading.RLock(); self.init()
    def connect(self):
        c = sqlite3.connect(self.path, timeout=10); c.row_factory = sqlite3.Row; c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA synchronous=NORMAL'); c.execute('PRAGMA foreign_keys=ON'); return c
    def init(self):
        with self.connect() as c: c.executescript(SCHEMA)
    def remember(self, content, kind='fact', importance=2, tags=None):
        now = time.time(); tag_text = ','.join(tags or [])
        with self._lock, self.connect() as c:
            cur = c.execute('INSERT INTO memories(content,kind,importance,tags,created_at,updated_at) VALUES(?,?,?,?,?,?)',(content,kind,importance,tag_text,now,now))
            row_id = cur.lastrowid
            c.execute('INSERT INTO memories_fts(rowid,content,tags) VALUES(?,?,?)',(row_id,content,tag_text))
            return row_id
    def search(self, query, limit=10):
        query = (query or '').strip()
        with self._lock, self.connect() as c:
            if query:
                tokens = ' '.join('"'+x.replace('"','')+'"' for x in query.split() if x.strip())
                rows = c.execute('SELECT m.* FROM memories m JOIN memories_fts f ON f.rowid=m.id WHERE memories_fts MATCH ? ORDER BY m.importance DESC,m.updated_at DESC LIMIT ?',(tokens,limit)).fetchall()
                if rows:
                    return [dict(r) for r in rows]
            rows = c.execute('SELECT * FROM memories ORDER BY importance DESC,updated_at DESC LIMIT ?',(limit,)).fetchall()
        return [dict(r) for r in rows]
    def forget(self, query):
        with self._lock, self.connect() as c:
            ids = [r['id'] for r in c.execute('SELECT id FROM memories WHERE lower(content) LIKE ? LIMIT 50',(f'%{query.lower()}%',)).fetchall()]
            for row_id in ids:
                c.execute('DELETE FROM memories_fts WHERE rowid=?',(row_id,)); c.execute('DELETE FROM memories WHERE id=?',(row_id,))
            return len(ids)
    def audit(self, action, permission, detail):
        with self.connect() as c: c.execute('INSERT INTO audit_events(action,permission,detail,created_at) VALUES(?,?,?,?)',(action,permission,detail,time.time()))
    def record_tool(self, tool,state,latency_ms,result):
        with self.connect() as c: c.execute('INSERT INTO tool_runs(tool,state,latency_ms,result,created_at) VALUES(?,?,?,?,?)',(tool,state,latency_ms,json.dumps(result,default=str)[:8000],time.time()))
    def save_python_task(self, task):
        with self.connect() as c:
            c.execute('INSERT INTO python_tasks(task_id,script,pid,status,started_at,ended_at,stdout,stderr,exit_code,working_directory) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET status=excluded.status,ended_at=excluded.ended_at,stdout=excluded.stdout,stderr=excluded.stderr,exit_code=excluded.exit_code', (task.get('task_id'),task.get('script'),task.get('pid'),task.get('status'),task.get('started_at'),task.get('ended_at'),task.get('stdout',''),task.get('stderr',''),task.get('exit_code'),task.get('working_directory')))
    def save_task(self,*values):
        with self.connect() as c:
            c.execute('INSERT INTO tasks(task_id,name,state,created_at,started_at,ended_at,progress,detail,error) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET name=excluded.name,state=excluded.state,started_at=excluded.started_at,ended_at=excluded.ended_at,progress=excluded.progress,detail=excluded.detail,error=excluded.error',values)
    def load_scheduled(self):
        with self.connect() as c: return [json.loads(r['task_json']) for r in c.execute('SELECT task_json FROM scheduled_tasks').fetchall()]
    def save_scheduled(self, task):
        with self.connect() as c: c.execute('INSERT INTO scheduled_tasks(id,task_json,updated_at) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET task_json=excluded.task_json,updated_at=excluded.updated_at',(task['id'],json.dumps(task),time.time()))

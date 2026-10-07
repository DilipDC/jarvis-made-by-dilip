from __future__ import annotations
import csv, hashlib, json, re, zipfile, time, os
from pathlib import Path
from xml.etree import ElementTree as ET
class RAGManager:
    def __init__(self,store):
        self.store=store
        self.semantic_enabled=os.getenv("JARVIS_SEMANTIC_RAG","0").lower() in {"1","true","yes","on"}
        self._embedder=None
    def _semantic(self):
        if not self.semantic_enabled:return None
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder=SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self.semantic_enabled=False
        return self._embedder
    def _extract(self,path:Path):
        if path.suffix.lower()=='.pdf':
            from pypdf import PdfReader; return '\n'.join((p.extract_text() or '') for p in PdfReader(str(path)).pages)
        if path.suffix.lower()=='.docx':
            with zipfile.ZipFile(path) as z: root=ET.fromstring(z.read('word/document.xml'))
            return '\n'.join(t.text or '' for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        if path.suffix.lower()=='.csv':
            with path.open(newline='',encoding='utf-8',errors='ignore') as f: return '\n'.join(' | '.join(row) for row in csv.reader(f))
        return path.read_text(encoding='utf-8',errors='ignore')
    def ingest(self,path):
        p=Path(path).expanduser().resolve(); text=self._extract(p); chunks=[text[i:i+1800] for i in range(0,len(text),1500)] or ['']; now=time.time(); meta=json.dumps({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        with self.store.connect() as c:
            row=c.execute('SELECT id FROM documents WHERE path=?',(str(p),)).fetchone()
            if row:
                doc_id=row['id']; old_ids=[x['id'] for x in c.execute('SELECT id FROM document_chunks WHERE document_id=?',(doc_id,)).fetchall()];
                for cid in old_ids: c.execute('DELETE FROM document_fts WHERE chunk_id=?',(cid,))
                c.execute('DELETE FROM document_chunks WHERE document_id=?',(doc_id,)); c.execute('UPDATE documents SET title=?,metadata=?,updated_at=? WHERE id=?',(p.name,meta,now,doc_id))
            else:
                cur=c.execute('INSERT INTO documents(path,title,metadata,created_at,updated_at) VALUES(?,?,?,?,?)',(str(p),p.name,meta,now,now)); doc_id=cur.lastrowid
            for i,ch in enumerate(chunks):
                cur=c.execute('INSERT INTO document_chunks(document_id,chunk_index,content,metadata) VALUES(?,?,?,?)',(doc_id,i,ch,meta)); c.execute('INSERT INTO document_fts(content,chunk_id) VALUES(?,?)',(ch,cur.lastrowid))
        return {'document':str(p),'chunks':len(chunks),'sha256':json.loads(meta)['sha256']}
    def search(self,q,limit=8):
        tokens=[re.sub(r'[^A-Za-z0-9_]', '',x) for x in q.split()]; query=' OR '.join(x for x in tokens if x)
        if not query: return []
        candidate_limit=max(limit*4,32) if self.semantic_enabled else limit
        with self.store.connect() as c:
            rows=c.execute('SELECT chunk_id,content FROM document_fts WHERE document_fts MATCH ? LIMIT ?',(query,candidate_limit)).fetchall()
        results=[dict(r) for r in rows]
        model=self._semantic()
        if model and results:
            try:
                vectors=model.encode([q]+[x["content"] for x in results],normalize_embeddings=True)
                qv=vectors[0]
                scored=[]
                for item,v in zip(results,vectors[1:]):
                    score=sum(float(a)*float(b) for a,b in zip(qv,v))
                    scored.append((score,item))
                scored.sort(key=lambda x:x[0],reverse=True)
                return [item for _,item in scored[:limit]]
            except Exception:
                pass
        return results[:limit]

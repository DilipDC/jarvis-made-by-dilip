from __future__ import annotations
import re
class ModelRouter:
    def __init__(self,general_model,coding_model):self.general_model=general_model; self.coding_model=coding_model
    def classify(self,text):
        if re.search(r"\b(code|coding|debug|bug|python|javascript|typescript|sql|api|refactor|repository|github)\b",text,re.I):return "coding"
        if re.search(r"\b(search|research|latest|current|news|documentation|source)\b",text,re.I):return "research"
        if re.search(r"\b(plan|steps|multi-step|build|implement)\b",text,re.I):return "planning"
        return "general"
    def route(self,text):return self.coding_model if self.classify(text)=="coding" else self.general_model

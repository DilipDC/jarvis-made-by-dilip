from __future__ import annotations
import importlib.util,os
class OpenAIAgentsAdapter:
    def __init__(self,model="gpt-5.6-luna"):self.model=model
    def status(self):
        enabled=os.getenv("OPENAI_ENABLED","false").lower() in {"1","true","yes","on"}
        return {"available":enabled and importlib.util.find_spec("agents") is not None and bool(os.getenv("OPENAI_API_KEY")),"enabled":enabled,"installed":importlib.util.find_spec("agents") is not None,"configured":bool(os.getenv("OPENAI_API_KEY")),"model":self.model}

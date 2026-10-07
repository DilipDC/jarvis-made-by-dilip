from pathlib import Path
from .engine import PolicyEngine
def load_policy(root="."):return PolicyEngine(Path(root)/"solution"/"restrictions.yaml")

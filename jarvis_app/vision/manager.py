from __future__ import annotations
import importlib.util
class VisionManager:
    def health(self): return {'opencv':bool(importlib.util.find_spec('cv2')),'pillow':bool(importlib.util.find_spec('PIL')),'lazy':True}

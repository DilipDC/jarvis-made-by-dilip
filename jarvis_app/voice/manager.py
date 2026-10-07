from __future__ import annotations
import importlib.util
class VoiceManager:
    def health(self):
        return {'stt':bool(importlib.util.find_spec('speech_recognition')),'tts':bool(importlib.util.find_spec('pyttsx3'))}

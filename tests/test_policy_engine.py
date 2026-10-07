from jarvis_app.policy.engine import PolicyEngine

def test_policy_modes(tmp_path):
    p=tmp_path/"restrictions.yaml"; p.write_text("""
version: 1
defaults:
  confirmation: confirm
actions:
  read_file:
    mode: allow
  execute_python:
    mode: confirm
  delete_file:
    mode: deny
""",encoding="utf-8")
    e=PolicyEngine(p); assert e.evaluate("read_file").level=="allow"; assert e.evaluate("execute_python").level=="confirm"; assert e.evaluate("delete_file").level=="deny"

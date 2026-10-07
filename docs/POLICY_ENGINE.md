# Policy engine

High-impact actions use `solution/restrictions.yaml`.

Modes:
- allow
- confirm
- deny

The runtime maps them to SAFE, CONFIRM and BLOCKED decisions and reloads the policy when the file changes.

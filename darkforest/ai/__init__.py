"""AI 决策层。

约束（见 docs/04）：
- **只通过 ``core.api`` 行动**，不许直接改 ``energy`` / ``hp``；
- 所有随机走 ``g.rng``，保证同种子可复现；
- 本包与 ``core`` 一样，**禁止 import pygame**。

负责人：④
"""

from __future__ import annotations

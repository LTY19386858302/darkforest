"""三体纪元·黑暗森林 —— Python 复刻版。

包结构约定（详见 docs/01-总纲）：

    darkforest.core  规则与状态，**禁止 import pygame**
    darkforest.ai    AI 决策，只通过 core.api 行动
    darkforest.ui    pygame 呈现层
    darkforest.net   联机
    darkforest.server 中继服务端

对外公开的入口只有两个：
    - ``from darkforest.core.api import ...``   规则层唯一门面
    - ``python -m darkforest``                  启动程序
"""

from __future__ import annotations

__version__ = "0.0.1"
__all__ = ["__version__"]

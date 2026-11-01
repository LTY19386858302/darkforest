"""联机层：协议、客户端、快照、大厅。

模块规划（见 docs/06）：
    client.py    9 个接口 + 长轮询
    protocol.py  10 种消息
    snapshot.py  按视角裁剪快照
    lobby.py     大厅状态机
    service.py   房主侧：执行指令、推进回合

负责人：⑥
"""

from __future__ import annotations

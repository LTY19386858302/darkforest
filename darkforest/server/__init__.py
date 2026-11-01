"""中继服务端：``server.js`` 的 Python 复刻。

要点（见 docs/06 第 6 节）：
- 标准库 ``ThreadingHTTPServer``，零依赖；
- 长轮询用 ``threading.Condition``，不要 ``time.sleep`` 空转；
- CORS 头 + ``OPTIONS → 204`` 一个都不能少（网页版是 file:// 打开的）。

负责人：⑥
"""

from __future__ import annotations

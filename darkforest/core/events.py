"""事件层：规则层与 UI 之间**唯一**的通道。

为什么不用全局 EventBus
----------------------
全局事件总线（`subscribe` / `publish`）会让"谁改了什么"变得不可追踪，
而且规则层一旦能主动 `publish`，它就能反过来影响 UI 状态——这正是原版
"规则与渲染强耦合"的病根。

这里采用最简单的单向模型：

    规则函数  ->  return [GameEvent, ...]  ->  UI 消费

规则层不持有任何 UI 引用；UI 决定怎么显示、显示给谁。
好处：规则可单测、可回放、可跑在无显示器环境（服务端 / CI / 平衡模拟）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventKind(StrEnum):
    LOG = "log"            # 写进日志面板
    TOAST = "toast"        # 短暂提示
    REFRESH = "refresh"    # 请求 UI 刷新（顶栏 / 面板）
    SOUND = "sound"        # 音效提示
    GAMEOVER = "gameover"  # 结算
    MODAL = "modal"        # 请求打开弹窗（如科技突破）


# 日志分类，对应原版 addLog 的第二个参数
LOG_EVT = "evt"     # 普通事件（灰）
LOG_GOOD = "good"   # 好消息（绿）
LOG_BAD = "bad"     # 坏消息（红）
LOG_WARN = "warn"   # 警告（黄）


@dataclass(frozen=True, slots=True)
class GameEvent:
    """一条事件。规则层只造它，不处理它。"""

    kind: EventKind
    text: str = ""
    cls: str = LOG_EVT
    civ_id: int | None = None      # 归属文明；None 表示"公开可见"
    payload: dict[str, Any] = field(default_factory=dict)

    # ---- 构造快捷方式（规则层用这些，别直接 new）----
    @staticmethod
    def log(text: str, cls: str = LOG_EVT, civ_id: int | None = None) -> "GameEvent":
        return GameEvent(EventKind.LOG, text=text, cls=cls, civ_id=civ_id)

    @staticmethod
    def toast(text: str) -> "GameEvent":
        return GameEvent(EventKind.TOAST, text=text)

    @staticmethod
    def refresh() -> "GameEvent":
        return GameEvent(EventKind.REFRESH)

    @staticmethod
    def gameover(win: bool, title: str, desc: str) -> "GameEvent":
        return GameEvent(EventKind.GAMEOVER, text=desc,
                         payload={"win": win, "title": title})

    @staticmethod
    def modal(name: str) -> "GameEvent":
        return GameEvent(EventKind.MODAL, payload={"name": name})


class EventBus:
    """事件收集器：规则层往里塞，UI 每帧取一次。

    刻意做成"队列 + 历史"而不是"订阅回调"——回调会让调用栈难以调试，
    而队列天然支持"这一帧发生了什么"的快照式读取。
    """

    __slots__ = ("_pending", "_history", "_cap")

    def __init__(self, cap: int = 200) -> None:
        self._pending: list[GameEvent] = []
        self._history: list[GameEvent] = []
        self._cap = cap

    # ---- 生产端（规则层）----
    def emit(self, *events: GameEvent) -> None:
        for ev in events:
            if ev is None:
                continue
            self._pending.append(ev)

    def emit_many(self, events: list[GameEvent] | None) -> None:
        if events:
            self._pending.extend(events)

    # ---- 消费端（UI）----
    def drain(self) -> list[GameEvent]:
        """取走自上次调用以来的全部事件。"""
        out, self._pending = self._pending, []
        self._history.extend(out)
        if len(self._history) > self._cap:
            del self._history[: len(self._history) - self._cap]
        return out

    def peek(self) -> list[GameEvent]:
        return list(self._pending)

    def history(self, limit: int | None = None) -> list[GameEvent]:
        return self._history[-limit:] if limit else list(self._history)

    def clear(self) -> None:
        self._pending.clear()
        self._history.clear()


def format_log(ev: GameEvent) -> str:
    """日志面板的单行文本。UI 也可以自己排版，这里给个兜底。"""
    prefix = {
        LOG_GOOD: "✔ ",
        LOG_BAD: "✘ ",
        LOG_WARN: "⚠ ",
    }.get(ev.cls, "")
    return f"{prefix}{ev.text}"

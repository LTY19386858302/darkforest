"""可种子化的随机源。

原版用无种子的 ``Math.random()``，同一个存档读两次结果不同。Python 版改成
"每局一个 Rng"，种子写进存档，换来两个好处：

1. 读档后 AI 行为可复现，方便做回归测试；
2. 平衡模拟（tools/balance.py）可以用固定种子做对照实验。

**规则层与 AI 层禁止直接 ``import random``**，一律走 ``g.rng``。
"""

from __future__ import annotations

import random
from collections.abc import MutableSequence, Sequence
from typing import TypeVar

T = TypeVar("T")


class Rng:
    """``random.Random`` 的薄封装，语义对齐原版几个工具函数。"""

    __slots__ = ("seed", "_r")

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self._r = random.Random(seed)

    # ---- 原版 rand(a, b)：闭开区间 ----
    def rand(self, a: float, b: float) -> float:
        return a + self._r.random() * (b - a)

    # ---- 原版 randInt(a, b)：**闭区间**，注意与 rand 不同 ----
    def randint(self, a: int, b: int) -> int:
        if b < a:
            a, b = b, a
        return self._r.randint(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        return seq[self._r.randrange(len(seq))]

    def shuffle(self, seq: MutableSequence[T]) -> None:
        self._r.shuffle(seq)

    def weighted_sample(self, pool: Sequence[T], n: int, weight_key: str = "weight") -> list[T]:
        """按 weight 字段无放回抽样。原版 ``weightedSample``（第 948 行）。"""
        def weight_of(item: object) -> float:
            if isinstance(item, dict):
                return float(item.get(weight_key, 1.0) or 0.0)
            return float(getattr(item, weight_key, 1.0) or 0.0)

        rest = list(pool)
        out: list[T] = []
        while len(out) < n and rest:
            total = sum(weight_of(p) for p in rest)
            if total <= 0:
                break
            pick = self._r.random() * total
            acc = 0.0
            for i, p in enumerate(rest):
                acc += weight_of(p)
                if pick <= acc:
                    out.append(rest.pop(i))
                    break
        return out

    def reseed(self, seed: int) -> None:
        self.seed = seed
        self._r.seed(seed)

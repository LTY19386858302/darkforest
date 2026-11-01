"""六边形几何：轴向坐标（axial）与屏幕像素互转。

原版对应：HTML 第 787–799 行。

坐标系约定
----------
尖顶朝上（pointy-top），轴向坐标 ``(q, r)``，第三轴 ``s = -q - r``。
这是原版使用的坐标，**不要换成 offset 坐标**——地图生成、距离、渲染全都基于它。

    pixel(q, r) = (S * 1.5 * q,  S * sqrt(3) * (r + q / 2))

其中 ``S`` 是六边形外接圆半径（原版常量 ``S = 46``）。
"""

from __future__ import annotations

import math
from collections.abc import Iterator

SQRT3 = math.sqrt(3.0)

#: 六边形边长（像素）。原版常量 ``S``。
SIDES = 46

#: 六个邻居方向。顺序即原版 ``DIRS``，画图和遍历都依赖这个顺序。
DIRS: tuple[tuple[int, int], ...] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)

Coord = tuple[int, int]


def key(q: int, r: int) -> Coord:
    """格子键。原版用 ``"q,r"`` 字符串，Python 用元组更快。"""
    return (q, r)


def neighbor_list(q: int, r: int) -> list[Coord]:
    return [(q + dq, r + dr) for dq, dr in DIRS]


def dist(q1: int, r1: int, q2: int, r2: int) -> int:
    """两格之间的六边形距离。"""
    dq, dr = q1 - q2, r1 - r2
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


def axial_round(qf: float, rf: float) -> Coord:
    """浮点轴向坐标 → 最近的整数格。

    原版对应 ``hexRound``（第 795–797 行）。三分支判断必须原样保留，
    否则点在格子边缘时会选错格，玩家会觉得"操作不跟手"。
    """
    sf = -qf - rf
    q, r, s = round(qf), round(rf), round(sf)
    dq, dr, ds = abs(q - qf), abs(r - rf), abs(s - sf)
    if dq > dr and dq > ds:
        q = -r - s
    elif dr > ds:
        r = -q - s
    return (q, r)


def pixel(q: int, r: int, side: float = SIDES) -> tuple[float, float]:
    """格子中心的世界像素坐标。"""
    return (side * 1.5 * q, side * SQRT3 * (r + q / 2))


def pixel_to_hex(x: float, y: float, side: float = SIDES) -> Coord:
    """世界像素坐标 → 格子。鼠标拾取用。"""
    qf = (2.0 / 3.0 * x) / side
    rf = (-1.0 / 3.0 * x + SQRT3 / 3.0 * y) / side
    return axial_round(qf, rf)


def corners(cx: float, cy: float, side: float = SIDES) -> list[tuple[float, float]]:
    """六个顶点，用于绘制。角度从 30° 起，保证尖顶朝上。"""
    return [
        (cx + side * math.cos(math.radians(60 * i + 30)),
         cy + side * math.sin(math.radians(60 * i + 30)))
        for i in range(6)
    ]


def iter_map_cells(map_r: int) -> Iterator[Coord]:
    """遍历半径 ``map_r`` 的六边形大盘上的全部格子。

    总格数 = ``3R^2 + 3R + 1``；R=20 → 1261，R=28 → 2437。
    """
    for q in range(-map_r, map_r + 1):
        for r in range(max(-map_r, -q - map_r), min(map_r, -q + map_r) + 1):
            yield (q, r)


def map_cell_count(map_r: int) -> int:
    return 3 * map_r * map_r + 3 * map_r + 1


def ring(center: Coord, radius: int) -> list[Coord]:
    """以 ``center`` 为中心、半径恰为 ``radius`` 的一圈格子。"""
    if radius <= 0:
        return [center]
    q0, r0 = center
    out: list[Coord] = []
    q, r = q0 + DIRS[4][0] * radius, r0 + DIRS[4][1] * radius
    for dq, dr in DIRS:
        for _ in range(radius):
            out.append((q, r))
            q += dq
            r += dr
    return out

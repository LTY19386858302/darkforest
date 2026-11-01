"""一个手搓的迷你世界，用于在 ② 完成世界生成之前跑通所有连线。

用途
----
- ``python -m darkforest --smoke``    验证 import 图与事件链路
- ``python -m darkforest --demo``     给 ⑤ 一个能画的东西（不用等世界生成）
- 单测里的 fixture

**它不是世界生成器**。真正的 ``start_game()`` 在 ② 手里。
"""

from __future__ import annotations

from .events import GameEvent
from .hex import iter_map_cells
from .rng import Rng
from .rules import MAP_SIZES, STARS
from .state import Civ, Game, Galaxy, Tile, Unit


def make_demo_game(seed: int = 42) -> Game:
    """造一张 2 个星系、2 个文明、5 个格子的迷你星图。"""
    map_r = 5
    g = Game(
        turn=1,
        map_r=map_r,
        size_key="tiny",
        seed=seed,
        rng=Rng(seed),
        cfg=MAP_SIZES["medium"],
        ai_strength="normal",
        pace=1.0,
    )

    for q, r in iter_map_cells(map_r):
        g.tiles[(q, r)] = Tile(q=q, r=r)

    # 星系 0：玩家的「太阳系」
    _make_galaxy(g, gid=0, name="太阳系", center=(0, 0),
                 planets=[((1, 0), "terran"), ((0, -1), "ocean"), ((-1, 0), "gas")])
    # 星系 1：AI 的「天狼星系」
    _make_galaxy(g, gid=1, name="天狼星系", center=(3, -2),
                 planets=[((4, -2), "terran"), ((3, -1), "desert")])

    player = Civ(id=0, name="人类", color="#4dd0e1", is_player=True,
                 energy=120.0, aggression=0.0, tech_rate=1.0, human=True)
    rival = Civ(id=1, name="三体文明", color="#e05555", energy=200.0,
                aggression=0.9, tech_rate=1.15, trait="科技至上，专制扩张")

    g.civs = [player, rival]

    # 玩家领土
    for q, r in ((0, 0), (1, 0), (0, -1)):
        t = g.tiles[(q, r)]
        t.owner = 0
    g.tiles[(0, 0)].pop = 0
    g.tiles[(1, 0)].pop = 3
    g.tiles[(0, -1)].pop = 1

    # AI 领土
    for q, r in ((3, -2), (4, -2)):
        g.tiles[(q, r)].owner = 1
    g.tiles[(4, -2)].pop = 3

    # 单位
    _spawn(g, unit_id=1, civ_id=0, type_="probe", q=1, r=0, moves=3)
    _spawn(g, unit_id=2, civ_id=0, type_="colony", q=1, r=0, moves=2)
    _spawn(g, unit_id=3, civ_id=1, type_="probe", q=4, r=-2, moves=3)
    g.next_uid = 4

    # 视野
    for q in range(-1, 3):
        for r in range(-2, 2):
            if (q, r) in g.tiles:
                g.explored.add((q, r))
    g.visible = set(g.explored)
    g.known_gal = {0}
    g.revealed = {(0, 0), (3, -2)}

    return g


def _make_galaxy(g: Game, gid: int, name: str, center: tuple[int, int],
                 planets: list[tuple[tuple[int, int], str]]) -> None:
    star = g.tiles[center]
    star.kind = "star"
    star.galaxy_id = gid
    star.star_type = STARS["yellow"].id
    for idx, ((q, r), ptype) in enumerate(planets, start=1):
        t = g.tiles[(q, r)]
        t.kind = "planet"
        t.galaxy_id = gid
        t.planet_type = ptype
        t.p_idx = idx
    g.galaxies.append(Galaxy(id=gid, name=name, q=center[0], r=center[1]))


def _spawn(g: Game, unit_id: int, civ_id: int, type_: str,
           q: int, r: int, moves: int) -> Unit:
    u = Unit(id=unit_id, civ_id=civ_id, type=type_, q=q, r=r, moves=moves)
    g.units.append(u)
    return u


def demo_events() -> list[GameEvent]:
    """演示事件链路：规则层造事件，UI 消费。"""
    return [
        GameEvent.log("你进入了小型星域：2 个星系散布在黑暗中。"),
        GameEvent.log("危机纪元元年。你的文明仰望星空，第一次意识到：不要回答。"),
        GameEvent.toast("事件总线已连通"),
    ]

"""规则层唯一门面（facade）。

**除 ``core`` 内部，任何人只许从这里 import。** UI、AI、net、server 都不直接
摸 ``economy`` / ``combat`` 这些实现模块——这样 ③ 重写内部实现时不会波及其他人的代码。

第 0 周的状态：函数签名齐全、抛 ``NotImplementedError``。
各模块落地后，把对应的 ``raise`` 换成一行 import 即可，调用方零改动。

    # 现在
    def civ_income(g, c): raise NotImplementedError(...)

    # ③ 做完之后
    from .economy import civ_income as _civ_income
    def civ_income(g, c): return _civ_income(g, c)
"""

from __future__ import annotations

from typing import Any

from .events import GameEvent
from .hex import Coord
from .state import Civ, Game, Income, Tile, Unit

__all__ = [
    # ② 内核
    "start_game", "next_turn", "to_json", "from_json", "validate_world",
    # ③ 规则
    "civ_income", "process_civ_turn", "build_turns", "begin_build", "build_with",
    "complete_build", "reach_map", "move_unit_to", "colonize", "power",
    "attack_unit", "attack_tile", "tile_defense", "capture_tile",
    "declare_war", "make_peace", "attitude_of",
    "do_broadcast", "process_strikes", "compute_fog",
    "check_elimination", "check_victory",
    # ④ AI
    "ai_turn", "steward_turn",
    # ⑥ 联机
    "snapshot_for",
]

_HINT = "第 0 周契约占位。实现后请把 raise 换成对真实模块的转发（见 docs/01 第 6 节）。"


def _todo(owner: str, module: str) -> NotImplementedError:
    return NotImplementedError(f"[{owner}] 尚未实现：{module}。{_HINT}")


# ============================================================ ② 内核
def start_game(size_key: str = "medium", ai_strength: str = "normal",
               pace: str = "normal", *, seed: int = 0) -> Game:
    """生成一局新游戏。owner: ② / core.worldgen.py"""
    raise _todo("②", "core/worldgen.start_game")


def next_turn(g: Game, *, player_id: int = 0) -> list[GameEvent]:
    """推进一个回合，返回期间产生的事件。owner: ② / core/turn.py"""
    raise _todo("②", "core/turn.next_turn")


def to_json(g: Game) -> dict[str, Any]:
    """序列化。owner: ② / core/save.to_json"""
    raise _todo("②", "core/save.to_json")


def from_json(d: dict[str, Any]) -> Game:
    """反序列化。owner: ② / core/save.from_json"""
    raise _todo("②", "core/save.from_json")


def validate_world(g: Game) -> list[str]:
    """世界合法性自检，返回问题列表（空 = 合法）。owner: ②"""
    raise _todo("②", "core/worldgen.validate_world")


# ============================================================ ③ 规则
def civ_income(g: Game, c: Civ) -> Income:
    """某文明的每回合产出。owner: ③ / core/economy.civ_income"""
    raise _todo("③", "core/economy.civ_income")


def process_civ_turn(g: Game, c: Civ) -> list[GameEvent]:
    """单文明结算：产出、维护费、科研、建造、人口。owner: ③"""
    raise _todo("③", "core/economy.process_civ_turn")


def build_turns(g: Game, t: Tile, kind: str, base: int, key: str) -> int:
    """建造所需回合数（含船坞/快速/曲率修正）。owner: ③"""
    raise _todo("③", "core/build.build_turns")


def begin_build(g: Game, t: Tile, kind: str, key: str) -> list[GameEvent]:
    """开始建造（普通速度）。owner: ③"""
    raise _todo("③", "core/build.begin_build")


def build_with(g: Game, t: Tile, kind: str, key: str,
               rush: bool = False, curv: bool = False) -> list[GameEvent]:
    """开始建造（可快速/可曲率）。owner: ③"""
    raise _todo("③", "core/build.build_with")


def complete_build(g: Game, t: Tile) -> list[GameEvent]:
    """结算一个已完工的建造项。owner: ③"""
    raise _todo("③", "core/build.complete_build")


def reach_map(g: Game, u: Unit) -> set[Coord]:
    """本单位本回合可达的格子集合。owner: ③ / core/units.reach_map"""
    raise _todo("③", "core/units.reach_map")


def move_unit_to(g: Game, u: Unit, q: int, r: int) -> list[GameEvent]:
    """移动单位。owner: ③"""
    raise _todo("③", "core/units.move_unit_to")


def colonize(g: Game, u: Unit) -> list[GameEvent]:
    """殖民。owner: ③"""
    raise _todo("③", "core/units.colonize")


def power(u: Unit) -> float:
    """单位战力 = combat * (0.3 + 0.7 * hp/100)。owner: ③"""
    raise _todo("③", "core/combat.power")


def attack_unit(g: Game, a: Unit, d: Unit) -> list[GameEvent]:
    """单位对拼。owner: ③"""
    raise _todo("③", "core/combat.attack_unit")


def attack_tile(g: Game, u: Unit, t: Tile) -> list[GameEvent]:
    """攻击地块。owner: ③"""
    raise _todo("③", "core/combat.attack_tile")


def tile_defense(g: Game, t: Tile) -> float:
    """地块防御力。owner: ③"""
    raise _todo("③", "core/combat.tile_defense")


def capture_tile(g: Game, civ_id: int, t: Tile) -> list[GameEvent]:
    """占领地块。owner: ③"""
    raise _todo("③", "core/combat.capture_tile")


def declare_war(g: Game, a: Civ, b: Civ) -> list[GameEvent]:
    """宣战。owner: ③"""
    raise _todo("③", "core/diplo.declare_war")


def make_peace(g: Game, a: Civ, b: Civ) -> list[GameEvent]:
    """议和。owner: ③"""
    raise _todo("③", "core/diplo.make_peace")


def attitude_of(g: Game, c: Civ) -> float:
    """AI 对玩家的态度值。owner: ③"""
    raise _todo("③", "core/diplo.attitude_of")


def do_broadcast(g: Game, src_gid: int, tgt_gid: int) -> list[GameEvent]:
    """引力波广播。owner: ③"""
    raise _todo("③", "core/darkforest.do_broadcast")


def process_strikes(g: Game) -> list[GameEvent]:
    """结算待处理的黑暗森林打击。owner: ③"""
    raise _todo("③", "core/darkforest.process_strikes")


def compute_fog(g: Game, civ_id: int = 0) -> None:
    """重算视野（写 g.visible / g.explored）。owner: ③"""
    raise _todo("③", "core/fog.compute_fog")


def check_elimination(g: Game) -> list[GameEvent]:
    """灭亡判定。owner: ③"""
    raise _todo("③", "core/victory.check_elimination")


def check_victory(g: Game, player_id: int = 0) -> list[GameEvent]:
    """胜负判定。owner: ③"""
    raise _todo("③", "core/victory.check_victory")


# ============================================================ ④ AI
def ai_turn(g: Game, c: Civ, *, player_id: int = 0) -> list[GameEvent]:
    """一个 AI 文明的完整回合。owner: ④ / ai/economy_ai.py"""
    raise _todo("④", "ai/economy_ai.ai_turn")


def steward_turn(g: Game, c: Civ) -> list[GameEvent]:
    """联机时代管离线玩家。owner: ④ / ai/steward.py"""
    raise _todo("④", "ai/steward.steward_turn")


# ============================================================ ⑥ 联机
def snapshot_for(g: Game, slot: int) -> dict[str, Any]:
    """生成发给某个 slot 的裁剪快照。owner: ⑥ / net/snapshot.py"""
    raise _todo("⑥", "net/snapshot.snapshot_for")

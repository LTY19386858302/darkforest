"""游戏状态的数据模型（契约）。

这些 dataclass 就是全队的"共同语言"。第 0 周冻结，之后改字段要走评审。

设计约束
--------
1. 所有可变状态都在 ``Game`` 里，禁止模块级全局变量。
   原版的 ``G`` / ``player`` / ``uid`` 三个全局变量是技术债，不要继承。
2. 全部 ``slots=True``：地图最多 3000 格 × 20 字段，用 ``__dict__`` 会多占约 3 倍内存。
3. ``Session`` 只属于当前客户端，**不进存档、不进联机快照**——
   否则客人会看到房主的选中框和相机位置。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .hex import Coord


@dataclass(slots=True)
class Income:
    """每回合产出。``civ_income()`` 的返回值。"""

    prod: float = 0.0
    sci: float = 0.0
    cul: float = 0.0
    pop: int = 0


@dataclass(slots=True)
class QueueItem:
    """建造队列项。``kind`` 是 ``"building"`` 或 ``"unit"``。"""

    kind: str
    key: str
    curvature: bool = False


@dataclass(slots=True)
class Tile:
    """一个六边形格子。行星、恒星、尘埃、虚空共用这一个结构。"""

    q: int
    r: int
    kind: str = "void"                    # void | star | planet | dust
    galaxy_id: int | None = None
    owner: int | None = None              # civ.id
    pop: int = 0
    buildings: list[str] = field(default_factory=list)
    queue: QueueItem | None = None
    hp: int = 100
    planet_type: str | None = None
    star_type: str | None = None
    ruined: bool = False
    p_idx: int = 0                        # 轨道序号，用于显示 Ⅰ/Ⅱ/Ⅲ
    activity: str | None = None           # culture | science | None
    fracture: bool = False                # 四维碎片
    fracture_born: int = 0
    fracture_life: int = 0
    fracture_used: bool = False
    prog: dict[str, int] = field(default_factory=dict)   # 建造进度，键 "b:xxx" / "u:xxx"
    paid: dict[str, bool] = field(default_factory=dict)
    rushed: dict[str, bool] = field(default_factory=dict)
    flattened: bool = False               # 被二向箔压平

    @property
    def coord(self) -> Coord:
        return (self.q, self.r)


@dataclass(slots=True)
class Civ:
    """一个文明。玩家与 AI 共用。"""

    id: int
    name: str
    color: str = "#4dd0e1"
    is_player: bool = False
    alive: bool = True

    # 性格（AI 用）
    aggression: float = 0.5
    tech_rate: float = 1.0
    trait: str = ""

    # 资源
    energy: float = 120.0
    sci: float = 0.0
    cul: float = 0.0
    energy_rate: float = 1.0              # AI 难度倍率；玩家恒为 1.0
    income: Income = field(default_factory=Income)

    # 科技
    researched: set[str] = field(default_factory=set)
    researching: str | None = None
    tech_prog: dict[str, float] = field(default_factory=dict)
    sci_bank: float = 0.0

    # 市政
    civic: str | None = None
    civ_prog: dict[str, float] = field(default_factory=dict)
    cul_bank: float = 0.0
    civics_done: set[str] = field(default_factory=set)
    policies: dict[str, str | None] = field(
        default_factory=lambda: {"eco": None, "mil": None, "sci": None}
    )

    # 威慑
    deterrence: float = 0.0
    deter_turns: int = 0

    # 外交
    war_with: set[int] = field(default_factory=set)
    wars: dict[str, int] = field(default_factory=dict)        # 键为对方 civ id 的字符串
    ceasefire: dict[str, int] = field(default_factory=dict)
    rel_p: float = 0.0
    peace_asked: int = 0
    hunt_boost: float = 0.0

    # 尤里卡
    eureka_fired: set[str] = field(default_factory=set)
    eureka_pending: set[str] = field(default_factory=set)

    # 联机
    human: bool = False                   # 真人玩家（含远端）
    ai_managed: bool = False              # 掉线后交给 AI 代管

    # 一次性日志标志（原版 sciConvLogged / culConvLogged）
    sci_conv_logged: bool = False
    cul_conv_logged: bool = False


@dataclass(slots=True)
class Unit:
    """一个舰队单位。"""

    id: int
    civ_id: int
    type: str
    q: int
    r: int
    hp: int = 100
    moves: int = 0
    num: int = 1
    goto: Coord | None = None
    fortified: bool = False
    sleeping: bool = False
    curvature: bool = False
    refit_turns: int = 0
    recuperate: int = 0
    derelict: bool = False                # 主人已灭亡 → 无主残骸
    fracture_power: bool = False


@dataclass(slots=True)
class Galaxy:
    """一个星系（恒星 + 行星）。"""

    id: int
    name: str
    q: int
    r: int
    dead: bool = False                    # 被光粒/二向箔摧毁


@dataclass(slots=True)
class MapConfig:
    """地图档位参数（源自 ``MAP_SIZES``）。"""

    label: str
    gal: int
    map_r: int
    min_d: int
    civs: int
    zoom: float


@dataclass(slots=True)
class MpState:
    """联机会话信息。只在联机时存在，随存档一起走。"""

    on: bool = False
    host: bool = False
    me: int = -1
    room: str = ""
    players: list[dict[str, Any]] = field(default_factory=list)
    alive: dict[int, bool] = field(default_factory=dict)
    ready: dict[int, bool] = field(default_factory=dict)
    host_offline: bool = False


@dataclass(slots=True)
class Game:
    """一局游戏的全部状态。"""

    turn: int = 1
    over: bool = False
    won: bool = False
    arks_launched: int = 0

    civs: list[Civ] = field(default_factory=list)
    galaxies: list[Galaxy] = field(default_factory=list)
    tiles: dict[Coord, Tile] = field(default_factory=dict)
    units: list[Unit] = field(default_factory=list)
    strikes: list[dict[str, Any]] = field(default_factory=list)

    explored: set[Coord] = field(default_factory=set)
    visible: set[Coord] = field(default_factory=set)
    met: set[int] = field(default_factory=lambda: {0})
    known_gal: set[int] = field(default_factory=set)
    revealed: set[Coord] = field(default_factory=set)

    logs: list[Any] = field(default_factory=list)
    plogs: dict[int, list[Any]] = field(default_factory=dict)

    cfg: MapConfig | None = None
    size_key: str = "medium"
    map_r: int = 20
    ai_strength: str = "normal"
    doom: bool = False
    pace: float = 1.0
    player_immune: bool = False

    colonized: int = 0
    unit_nums: dict[str, int] = field(default_factory=dict)
    next_uid: int = 1

    seed: int = 0
    rng: Any = None                       # core.rng.Rng，用 Any 避免循环引用

    mp: MpState | None = None

    # ---- 便捷访问 ----
    def civ(self, civ_id: int) -> Civ | None:
        for c in self.civs:
            if c.id == civ_id:
                return c
        return None

    def player(self) -> Civ | None:
        for c in self.civs:
            if c.is_player:
                return c
        return self.civs[0] if self.civs else None

    def tile(self, q: int, r: int) -> Tile | None:
        return self.tiles.get((q, r))

    def tiles_of(self, civ_id: int) -> list[Tile]:
        return [t for t in self.tiles.values() if t.owner == civ_id]

    def units_of(self, civ_id: int) -> list[Unit]:
        return [u for u in self.units if u.civ_id == civ_id]


@dataclass(slots=True)
class Session:
    """只属于当前客户端的状态：选中、相机、菜单弹窗。

    **不进存档、不进快照。** 混进 Game 会让联机时"别人操作把你的镜头拽走"。
    """

    sel_unit: Unit | None = None
    sel_tile: Tile | None = None
    move_mode: bool = False
    move_target: Coord | None = None
    pending_end: bool = False
    diplo_civ: int | None = None
    spectate: bool = False

    cam_x: float = 0.0
    cam_y: float = 0.0
    cam_zoom: float = 0.42

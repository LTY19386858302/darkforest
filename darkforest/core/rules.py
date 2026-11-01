"""常量表（数据，不是逻辑）。

原版对应：HTML 第 787–966 行。

第 0 周只搬"所有人都要用到"的四张表：地图档位、行星类型、恒星类型、单位类型。
科技 / 市政 / 政策 / 建筑四张表由 ③ 在 M3 补齐（结构已留好）。

**这些表只读**：运行时不许修改，否则联机快照会出现两边不一致。
"""

from __future__ import annotations

from dataclasses import dataclass

from .state import MapConfig

# ---------------------------------------------------------------- 地图档位
MAP_SIZES: dict[str, MapConfig] = {
    "small":  MapConfig("小型", gal=6,  map_r=17, min_d=10, civs=3, zoom=0.50),
    "medium": MapConfig("中型", gal=9,  map_r=20, min_d=10, civs=5, zoom=0.42),
    "large":  MapConfig("大型", gal=12, map_r=25, min_d=11, civs=6, zoom=0.34),
    "huge":   MapConfig("巨型", gal=15, map_r=28, min_d=11, civs=8, zoom=0.28),
}

#: 难度倍率（乘在 AI 文明的 energy_rate 上）
AI_ENERGY_RATES: dict[str, float] = {
    "low": 0.7, "normal": 1.0, "hard": 1.25, "brutal": 1.6, "doom": 2.0,
}

#: 难度侵略倍率（乘在 aggression 上，上限 1.5）
AI_AGGR_MULT: dict[str, float] = {
    "low": 1.0, "normal": 1.0, "hard": 1.0, "brutal": 1.0, "doom": 1.25,
}

#: 难度"不宣而战清理"每回合概率
AI_CLEAN_P: dict[str, float] = {
    "low": 0.12, "normal": 0.20, "hard": 0.26, "brutal": 0.32, "doom": 0.45,
}

#: 进程倍率（只影响能源/科技/文化产出）
PACE_RATES: dict[str, float] = {
    "slow": 0.5, "slower": 0.75, "normal": 1.0, "faster": 1.3, "fast": 1.7,
}
PACE_LABEL: dict[str, str] = {
    "slow": "慢 0.5×", "slower": "较慢 0.75×", "normal": "正常 1×",
    "faster": "较快 1.3×", "fast": "快 1.7×",
}


# ---------------------------------------------------------------- 行星 / 恒星
@dataclass(frozen=True, slots=True)
class PlanetType:
    id: str
    name: str
    color: str
    prod: int
    sci: int
    cap: int


PLANET_TYPES: dict[str, PlanetType] = {p.id: p for p in (
    PlanetType("terran", "类地行星", "#5ba86f", prod=2, sci=2, cap=5),
    PlanetType("desert", "荒漠行星", "#c2a36b", prod=2, sci=1, cap=3),
    PlanetType("ice",    "冰封行星", "#a8d8e8", prod=1, sci=2, cap=3),
    PlanetType("gas",    "气态巨行星", "#d8a86b", prod=3, sci=1, cap=2),
    PlanetType("ocean",  "海洋行星", "#4f86c2", prod=1, sci=3, cap=4),
    PlanetType("lava",   "熔岩行星", "#e0663d", prod=3, sci=0, cap=2),
    PlanetType("barren", "贫瘠行星", "#8a8a8a", prod=1, sci=1, cap=2),
)}

INNER_POOL: tuple[str, ...] = (
    "terran", "terran", "ocean", "desert", "lava", "barren", "ocean", "desert",
)
OUTER_POOL: tuple[str, ...] = (
    "gas", "gas", "ice", "ice", "ocean", "terran", "barren", "ice",
)


@dataclass(frozen=True, slots=True)
class StarType:
    id: str
    name: str
    color: str


STARS: dict[str, StarType] = {s.id: s for s in (
    StarType("yellow",  "黄矮星",   "#ffd76b"),
    StarType("red",     "红矮星",   "#ff7043"),
    StarType("blue",    "蓝巨星",   "#4fc3f7"),
    StarType("white",   "白矮星",   "#e8e8f0"),
    StarType("neutron", "中子星",   "#b388ff"),
    StarType("binary",  "双星系统", "#ffca28"),
)}


# ---------------------------------------------------------------- 单位
@dataclass(frozen=True, slots=True)
class UnitType:
    id: str
    name: str
    cost: int
    turns: int
    moves: int
    combat: int
    vision: int
    upkeep: int
    tag: str
    untargetable: bool = False
    one_shot: str | None = None       # "star" | "area" | None


UNIT_TYPES: dict[str, UnitType] = {u.id: u for u in (
    UnitType("probe",      "探测器",     cost=30,  turns=2, moves=3, combat=4,   vision=3, upkeep=1, tag="侦察"),
    UnitType("colony",     "殖民船",     cost=50,  turns=3, moves=2, combat=3,   vision=2, upkeep=1, tag="殖民"),
    UnitType("sophon",     "智子",       cost=80,  turns=3, moves=6, combat=1,   vision=5, upkeep=1, tag="侦察", untargetable=True),
    UnitType("ship1",      "行星级战舰", cost=90,  turns=3, moves=3, combat=15,  vision=2, upkeep=1, tag="战斗"),
    UnitType("ship2",      "恒星级战舰", cost=260, turns=5, moves=4, combat=45,  vision=2, upkeep=3, tag="战斗"),
    UnitType("droplet",    "水滴",       cost=330, turns=5, moves=4, combat=120, vision=2, upkeep=3, tag="决战"),
    UnitType("ark",        "星舰方舟",   cost=500, turns=8, moves=6, combat=35,  vision=2, upkeep=5, tag="方舟"),
    UnitType("lightbullet","光粒",       cost=350, turns=5, moves=5, combat=5,   vision=2, upkeep=2, tag="打击", one_shot="star"),
    UnitType("dualvector", "二向箔",     cost=700, turns=8, moves=3, combat=5,   vision=2, upkeep=2, tag="降维", untargetable=True, one_shot="area"),
)}

#: 曲率引擎只允许装在这三种船上
CURV_ALLOWED: tuple[str, ...] = ("colony", "ship1", "ship2")

# ---------------------------------------------------------------- 待 ③ 补齐
# 结构留好，M3 由 ③ 填充；在此之前 UI 只能显示"未实现"。
TECHS: dict[str, object] = {}        # 17 项科技
CIVICS: dict[str, object] = {}       # 7 项市政
POLICIES: dict[str, object] = {}     # 7 项政策
BUILDINGS: dict[str, object] = {}    # 14 项建筑

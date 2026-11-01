"""契约测试：接口必须齐全、必须带 owner 标记、必须抛 NotImplementedError。

这条测试的价值：任何人误把占位实现删掉/改签名，CI 立刻红，
而不是等到 ④ 的 AI 调 ③ 的函数时才发现参数对不上。
"""

from __future__ import annotations

import unittest

from darkforest.core import api

#: 第 0 周冻结的公开接口（docs/01 第 6.2 节）
EXPECTED = [
    "start_game", "next_turn", "to_json", "from_json", "validate_world",
    "civ_income", "process_civ_turn", "build_turns", "begin_build", "build_with",
    "complete_build", "reach_map", "move_unit_to", "colonize", "power",
    "attack_unit", "attack_tile", "tile_defense", "capture_tile",
    "declare_war", "make_peace", "attitude_of",
    "do_broadcast", "process_strikes", "compute_fog",
    "check_elimination", "check_victory",
    "ai_turn", "steward_turn",
    "snapshot_for",
]


class TestContract(unittest.TestCase):
    def test_all_exported(self) -> None:
        for name in EXPECTED:
            self.assertTrue(hasattr(api, name), f"api 缺少 {name}")
            self.assertIn(name, api.__all__, f"__all__ 缺少 {name}")

    def test_stubs_raise_with_owner(self) -> None:
        from darkforest.core.demo import make_demo_game

        g = make_demo_game()
        c = g.civs[0]
        u = g.units[0]
        t = g.tiles[(0, 0)]

        calls = {
            "next_turn": lambda: api.next_turn(g),
            "civ_income": lambda: api.civ_income(g, c),
            "power": lambda: api.power(u),
            "reach_map": lambda: api.reach_map(g, u),
            "tile_defense": lambda: api.tile_defense(g, t),
            "attitude_of": lambda: api.attitude_of(g, c),
            "ai_turn": lambda: api.ai_turn(g, c),
            "snapshot_for": lambda: api.snapshot_for(g, 0),
        }
        for name, call in calls.items():
            with self.subTest(name=name):
                with self.assertRaises(NotImplementedError) as ctx:
                    call()
                self.assertIn("docs/01", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

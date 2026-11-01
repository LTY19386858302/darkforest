"""命令行入口。

    python -m darkforest              # 启动图形界面（需要 pygame-ce）
    python -m darkforest --demo       # 用迷你世界启动，不依赖世界生成
    python -m darkforest --smoke      # 无头自检，CI 用（零第三方依赖）
    python -m darkforest --headless 20  # 无头跑 20 回合（M2 之后才有意义）
"""

from __future__ import annotations

import argparse
import sys
import traceback

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="darkforest",
        description="三体纪元·黑暗森林 —— Python 复刻版",
    )
    p.add_argument("--smoke", action="store_true",
                   help="无头自检：构造迷你世界、跑事件链路、校验接口契约")
    p.add_argument("--demo", action="store_true",
                   help="用内置迷你世界启动图形界面（不需要世界生成器）")
    p.add_argument("--headless", type=int, metavar="N", default=None,
                   help="无头模拟 N 个回合")
    p.add_argument("--size", default="medium",
                   choices=["small", "medium", "large", "huge"],
                   help="地图档位（--headless 用）")
    p.add_argument("--seed", type=int, default=0, help="随机种子")
    p.add_argument("--version", action="version", version=f"darkforest {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.smoke:
        return cmd_smoke()
    if args.headless is not None:
        return cmd_headless(args.headless, args.size, args.seed)
    return cmd_gui(demo=args.demo, seed=args.seed)


# ---------------------------------------------------------------- 自检
def cmd_smoke() -> int:
    """CI 用。任何一步失败立即返回非零，并打印出在哪一步。"""
    from .core import api
    from .core.demo import demo_events, make_demo_game
    from .core.events import EventBus
    from .core.hex import dist, iter_map_cells, map_cell_count, pixel, pixel_to_hex

    steps: list[tuple[str, bool, str]] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        steps.append((name, cond, detail))

    # 1) 世界
    try:
        g = make_demo_game(seed=7)
        check("demo 世界已构造", True, f"{len(g.tiles)} 格")
    except Exception:
        traceback.print_exc()
        print("[FAIL] demo 世界构造失败")
        return 1

    check("格子数符合公式", len(g.tiles) == map_cell_count(5),
          f"期望 {map_cell_count(5)}，实际 {len(g.tiles)}")
    check("星系数量", len(g.galaxies) == 2, f"{len(g.galaxies)} 个")
    check("文明数量", len(g.civs) == 2, f"{len(g.civs)} 个")
    check("单位都站在格子上",
          all((u.q, u.r) in g.tiles for u in g.units), f"{len(g.units)} 个单位")
    check("单位的主人都存在",
          all(g.civ(u.civ_id) is not None for u in g.units), "")
    check("恒星存在", any(t.kind == "star" for t in g.tiles.values()), "")

    # 2) 几何往返
    bad = [c for c in iter_map_cells(5)
           if pixel_to_hex(*pixel(*c)) != c]
    check("pixel→hex 往返无误差", not bad, f"{len(bad)} 个失败")
    check("距离对称", dist(0, 0, 3, -2) == dist(3, -2, 0, 0), "")
    check("自身距离为 0", dist(2, -1, 2, -1) == 0, "")

    # 3) 事件链路
    bus = EventBus()
    bus.emit(*demo_events())
    drained = bus.drain()
    check("事件总线收发正常", len(drained) == 3, f"收到 {len(drained)} 条")
    check("事件有分类", all(ev.kind for ev in drained), "")
    check("drain 后队列为空", bus.peek() == [], "")

    # 4) 契约占位：必须抛 NotImplementedError，且消息里带 owner
    try:
        api.next_turn(g)
    except NotImplementedError as e:
        ok = "②" in str(e)
        check("next_turn 是契约占位", ok, str(e)[:48])
    else:
        check("next_turn 是契约占位", False, "居然没抛异常")

    for name in ("civ_income", "ai_turn", "snapshot_for"):
        fn = getattr(api, name)
        check(f"api.{name} 已导出", callable(fn), "")

    # 5) 汇总
    failed = [s for s in steps if not s[1]]
    print(f"darkforest {__version__} · smoke")
    print("-" * 58)
    for name, ok, detail in steps:
        mark = "ok  " if ok else "FAIL"
        print(f"  [{mark}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 58)
    print(f"{len(steps) - len(failed)}/{len(steps)} 项通过")
    return 0 if not failed else 1


# ---------------------------------------------------------------- 无头
def cmd_headless(turns: int, size: str, seed: int) -> int:
    from .core import api
    from .core.events import EventBus

    print(f"darkforest {__version__} · headless {turns} 回合 · {size} · seed={seed}")
    try:
        g = api.start_game(size, "normal", "normal", seed=seed)
    except NotImplementedError as e:
        print(f"  [skip] {e}")
        print("  → 世界生成由 ② 负责，M1 之后这里才会真的跑起来。")
        return 0

    bus = EventBus()
    for _ in range(turns):
        bus.emit_many(api.next_turn(g, player_id=0))
        if g.over:
            break
    print(f"  完成 {g.turn - 1} 回合，{len(bus.drain())} 条事件")
    return 0


# ---------------------------------------------------------------- 图形界面
def cmd_gui(demo: bool, seed: int) -> int:
    try:
        import pygame  # noqa: F401
    except ImportError:
        print("没有安装 pygame。请先执行：")
        print("    pip install pygame-ce")
        print("或者用无头自检：python -m darkforest --smoke")
        return 2

    from .ui.app import run

    if demo:
        from .core.demo import make_demo_game
        return run(make_demo_game(seed=seed), title="黑暗森林 · DEMO")

    from .core import api
    try:
        g = api.start_game("medium", "normal", "normal", seed=seed)
    except NotImplementedError:
        print("世界生成尚未实现（② 负责）。先用 --demo 看骨架效果：")
        print("    python -m darkforest --demo")
        return 2
    return run(g, title="黑暗森林")


if __name__ == "__main__":
    sys.exit(main())

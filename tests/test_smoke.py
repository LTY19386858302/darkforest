"""端到端冒烟：CLI 入口能不能跑通。

两种测法：

1. **进程内调用** ``main([...])``——覆盖 argparse + 业务逻辑，零子进程开销；
2. **真起一个子进程**——覆盖 "python -m darkforest" 这条路，但某些受限沙箱
   不允许管道捕获，此时 skip 而不是 fail。

CI 里还会单独跑一次 ``python -m darkforest --smoke``（见 .github/workflows/ci.yml），
所以即使第 2 种被 skip，覆盖也不会丢。
"""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path

from darkforest.__main__ import main
from darkforest.core.demo import make_demo_game

ROOT = Path(__file__).resolve().parent.parent


def run_cli(argv: list[str]) -> tuple[int, str]:
    """进程内跑 CLI，返回 (退出码, 标准输出)。"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


class TestCliInProcess(unittest.TestCase):
    def test_smoke(self) -> None:
        code, out = run_cli(["--smoke"])
        self.assertEqual(code, 0, out)
        self.assertIn("项通过", out)

    def test_version(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as ctx:
            main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("darkforest", buf.getvalue().lower())

    def test_headless_degrades_gracefully(self) -> None:
        """世界生成还没实现时，--headless 给提示而不是崩栈。"""
        code, out = run_cli(["--headless", "3"])
        self.assertEqual(code, 0, out)
        self.assertTrue("[skip]" in out or "完成" in out, out)

    def test_unknown_map_size_rejected(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(io.StringIO()):
                main(["--size", "galactic"])
        self.assertNotEqual(ctx.exception.code, 0)


class TestCliSubprocess(unittest.TestCase):
    def test_module_entry(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "darkforest", "--smoke"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if proc.stdout is None:
            self.skipTest("当前沙箱不允许捕获子进程输出；CI 里会单独跑这条命令")
        self.assertEqual(proc.returncode, 0, proc.stdout + (proc.stderr or ""))
        self.assertIn("项通过", proc.stdout)


class TestDemoWorld(unittest.TestCase):
    def test_invariants(self) -> None:
        g = make_demo_game()
        self.assertEqual(len(g.galaxies), 2)
        self.assertEqual(len(g.civs), 2)
        self.assertTrue(all((u.q, u.r) in g.tiles for u in g.units))
        self.assertTrue(all(g.civ(u.civ_id) for u in g.units))
        self.assertEqual(len({c.id for c in g.civs}), len(g.civs))

    def test_deterministic(self) -> None:
        a, b = make_demo_game(seed=99), make_demo_game(seed=99)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(len(a.tiles), len(b.tiles))
        self.assertEqual([(t.q, t.r) for t in a.tiles.values()],
                         [(t.q, t.r) for t in b.tiles.values()])

    def test_units_have_no_duplicate_ids(self) -> None:
        g = make_demo_game()
        ids = [u.id for u in g.units]
        self.assertEqual(len(ids), len(set(ids)))

    def test_next_uid_ahead_of_all_units(self) -> None:
        g = make_demo_game()
        self.assertGreaterEqual(g.next_uid, max(u.id for u in g.units) + 1)


if __name__ == "__main__":
    unittest.main()

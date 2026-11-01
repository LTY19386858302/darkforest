"""事件总线的回归测试。"""

from __future__ import annotations

import unittest

from darkforest.core.events import (
    LOG_BAD,
    LOG_GOOD,
    EventBus,
    EventKind,
    GameEvent,
    format_log,
)


class TestGameEvent(unittest.TestCase):
    def test_factory_helpers(self) -> None:
        self.assertEqual(GameEvent.log("hi").kind, EventKind.LOG)
        self.assertEqual(GameEvent.toast("hi").kind, EventKind.TOAST)
        self.assertEqual(GameEvent.refresh().kind, EventKind.REFRESH)

    def test_gameover_payload(self) -> None:
        ev = GameEvent.gameover(True, "统治胜利", "森林里只剩你")
        self.assertTrue(ev.payload["win"])
        self.assertEqual(ev.payload["title"], "统治胜利")

    def test_frozen(self) -> None:
        ev = GameEvent.log("x")
        with self.assertRaises(Exception):
            ev.text = "y"  # type: ignore[misc]

    def test_format_log_prefix(self) -> None:
        self.assertTrue(format_log(GameEvent.log("a", LOG_GOOD)).startswith("✔"))
        self.assertTrue(format_log(GameEvent.log("a", LOG_BAD)).startswith("✘"))
        self.assertEqual(format_log(GameEvent.log("a")).strip(), "a")


class TestEventBus(unittest.TestCase):
    def test_emit_then_drain(self) -> None:
        bus = EventBus()
        bus.emit(GameEvent.log("a"), GameEvent.log("b"))
        self.assertEqual(len(bus.peek()), 2)
        self.assertEqual(len(bus.drain()), 2)
        self.assertEqual(bus.peek(), [])

    def test_emit_many_handles_none(self) -> None:
        bus = EventBus()
        bus.emit_many(None)
        bus.emit_many([GameEvent.log("a")])
        self.assertEqual(len(bus.drain()), 1)

    def test_history_is_capped(self) -> None:
        bus = EventBus(cap=5)
        for i in range(20):
            bus.emit(GameEvent.log(str(i)))
            bus.drain()
        self.assertEqual(len(bus.history()), 5)
        self.assertEqual(bus.history()[-1].text, "19")

    def test_history_limit(self) -> None:
        bus = EventBus()
        for i in range(4):
            bus.emit(GameEvent.log(str(i)))
        bus.drain()
        self.assertEqual(len(bus.history(2)), 2)


if __name__ == "__main__":
    unittest.main()

"""六边形几何的回归测试。用 unittest 写，保证零依赖也能跑。

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import math
import unittest

from darkforest.core.hex import (
    SIDES,
    corners,
    dist,
    iter_map_cells,
    map_cell_count,
    neighbor_list,
    pixel,
    pixel_to_hex,
    ring,
)


class TestDist(unittest.TestCase):
    def test_self_is_zero(self) -> None:
        for q, r in ((0, 0), (3, -2), (-4, 1)):
            self.assertEqual(dist(q, r, q, r), 0)

    def test_symmetric(self) -> None:
        self.assertEqual(dist(0, 0, 3, -2), dist(3, -2, 0, 0))

    def test_unit_neighbors_are_one(self) -> None:
        for q, r in neighbor_list(2, -1):
            self.assertEqual(dist(2, -1, q, r), 1)

    def test_known_values(self) -> None:
        self.assertEqual(dist(0, 0, 4, 0), 4)
        self.assertEqual(dist(0, 0, 0, 4), 4)
        self.assertEqual(dist(0, 0, 4, -4), 4)
        # (2,-1) 不是邻居，它在两格之外（轴向坐标的直觉陷阱）
        self.assertEqual(dist(0, 0, 2, -1), 2)


class TestPixelRoundTrip(unittest.TestCase):
    def test_all_cells_roundtrip(self) -> None:
        for q, r in iter_map_cells(6):
            x, y = pixel(q, r)
            self.assertEqual(pixel_to_hex(x, y), (q, r), f"({q},{r}) 往返失败")

    def test_offset_still_nearest(self) -> None:
        """格心附近 8px 内的点，仍应落到同一格。"""
        for q, r in ((0, 0), (3, -2), (-2, 5)):
            x, y = pixel(q, r)
            for dx, dy in ((8, 0), (-8, 0), (0, 8), (0, -8), (6, 6)):
                self.assertEqual(pixel_to_hex(x + dx, y + dy), (q, r))

    def test_pixel_formula(self) -> None:
        x, y = pixel(1, 0)
        self.assertAlmostEqual(x, SIDES * 1.5)
        self.assertAlmostEqual(y, SIDES * math.sqrt(3) * 0.5)


class TestMapShape(unittest.TestCase):
    def test_cell_count_matches_formula(self) -> None:
        for map_r in (0, 1, 5, 12, 20):
            self.assertEqual(len(list(iter_map_cells(map_r))), map_cell_count(map_r))

    def test_cells_within_radius(self) -> None:
        for q, r in iter_map_cells(8):
            self.assertLessEqual(dist(0, 0, q, r), 8)

    def test_ring_size(self) -> None:
        self.assertEqual(len(ring((0, 0), 0)), 1)
        for radius in (1, 2, 3):
            self.assertEqual(len(ring((0, 0), radius)), 6 * radius)

    def test_corners(self) -> None:
        pts = corners(0.0, 0.0)
        self.assertEqual(len(pts), 6)
        for x, y in pts:
            self.assertAlmostEqual(math.hypot(x, y), SIDES)


if __name__ == "__main__":
    unittest.main()

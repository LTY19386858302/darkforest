"""最小可用的 pygame 客户端骨架。

它只做四件事，目的是让 ⑤ 有个能改的起点、让全队能看到"星图长什么样"：

1. 打开窗口、跑 60fps 主循环
2. 把六边形网格画出来（按地形/归属上色）
3. 支持拖动平移、滚轮缩放（以鼠标为锚点）
4. 顶栏显示状态文字

**没有**：单位图标、面板、弹窗、输入状态机——那些是 ⑤ 的 T5.5–T5.13。
"""

from __future__ import annotations

import pygame

from ..core.hex import SIDES, corners, pixel, pixel_to_hex
from ..core.rules import PLANET_TYPES
from ..core.state import Game

# ---- 配色（先硬编码，M2 后迁到 ui/theme.py）----
BG = (4, 6, 13)
VOID_SHADES = ((11, 16, 29), (12, 19, 35), (10, 15, 27))
GRID = (38, 54, 90)
DUST = (58, 52, 34)
TEXT = (219, 228, 240)
DIM = (138, 151, 173)
CYAN = (77, 208, 225)


class Camera:
    """平移 + 缩放。屏幕↔世界坐标互转。"""

    __slots__ = ("x", "y", "zoom")

    def __init__(self, x: float, y: float, zoom: float) -> None:
        self.x = x
        self.y = y
        self.zoom = zoom

    def world_to_screen(self, wx: float, wy: float, vw: int, vh: int) -> tuple[float, float]:
        return (vw / 2 + (wx - self.x) * self.zoom,
                vh / 2 + (wy - self.y) * self.zoom)

    def screen_to_world(self, sx: float, sy: float, vw: int, vh: int) -> tuple[float, float]:
        return (self.x + (sx - vw / 2) / self.zoom,
                self.y + (sy - vh / 2) / self.zoom)


def tile_color(g: Game, q: int, r: int) -> tuple[int, int, int]:
    t = g.tiles.get((q, r))
    if t is None:
        return VOID_SHADES[(q * 7 + r * 13) % 3]
    if t.kind == "dust":
        return DUST
    if t.owner is not None:
        c = g.civ(t.owner)
        if c and c.color.startswith("#") and len(c.color) == 7:
            return (int(c.color[1:3], 16) // 3 + 40,
                    int(c.color[3:5], 16) // 3 + 40,
                    int(c.color[5:7], 16) // 3 + 40)
    if t.kind == "planet" and t.planet_type:
        pt = PLANET_TYPES.get(t.planet_type)
        if pt:
            return (int(pt.color[1:3], 16), int(pt.color[3:5], 16), int(pt.color[5:7], 16))
    return VOID_SHADES[(q * 7 + r * 13) % 3]


def draw_world(surf: pygame.Surface, g: Game, cam: Camera) -> None:
    vw, vh = surf.get_size()
    side = SIDES * cam.zoom
    if side < 3:
        return

    # 只遍历视口内的格子（性能命门，见 docs/05 第 4.3 节）
    x0, y0 = cam.screen_to_world(0, 0, vw, vh)
    x1, y1 = cam.screen_to_world(vw, vh, vw, vh)
    q_lo = int(x0 / (1.5 * SIDES)) - 1
    q_hi = int(x1 / (1.5 * SIDES)) + 1

    for q in range(q_lo, q_hi + 1):
        for r in range(-g.map_r - 2, g.map_r + 3):
            if (q, r) not in g.tiles:
                continue
            wx, wy = pixel(q, r)
            sx, sy = cam.world_to_screen(wx, wy, vw, vh)
            if sx < -side * 2 or sx > vw + side * 2 or sy < -side * 2 or sy > vh + side * 2:
                continue
            pts = corners(sx, sy, side)
            pygame.draw.polygon(surf, tile_color(g, q, r), pts)
            pygame.draw.polygon(surf, GRID, pts, 1)

    # 单位：小圆点（正式图标是 ⑤ 的活）
    for u in g.units:
        wx, wy = pixel(u.q, u.r)
        sx, sy = cam.world_to_screen(wx, wy, vw, vh)
        c = g.civ(u.civ_id)
        color = (200, 200, 220)
        if c and len(c.color) == 7:
            color = (int(c.color[1:3], 16), int(c.color[3:5], 16), int(c.color[5:7], 16))
        pygame.draw.circle(surf, color, (int(sx), int(sy)), max(3, int(6 * cam.zoom)))
        pygame.draw.circle(surf, BG, (int(sx), int(sy)), max(3, int(6 * cam.zoom)), 1)


def run(g: Game, title: str = "黑暗森林") -> int:
    pygame.init()
    screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    home = g.galaxies[0] if g.galaxies else None
    if home:
        wx, wy = pixel(home.q, home.r)
    else:
        wx = wy = 0.0
    cam = Camera(wx, wy, 0.9)

    font = pygame.font.SysFont("microsoftyahei,simhei,arial", 15)
    dragging = False
    last = (0, 0)

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                dragging = True
                last = ev.pos
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                dragging = False
            elif ev.type == pygame.MOUSEMOTION and dragging:
                dx, dy = ev.pos[0] - last[0], ev.pos[1] - last[1]
                if abs(dx) + abs(dy) > 0:
                    cam.x -= dx / cam.zoom
                    cam.y -= dy / cam.zoom
                    last = ev.pos
            elif ev.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                before = cam.screen_to_world(mx, my, *screen.get_size())
                cam.zoom = max(0.15, min(2.5, cam.zoom * (1.1 ** ev.y)))
                after = cam.screen_to_world(mx, my, *screen.get_size())
                cam.x += before[0] - after[0]
                cam.y += before[1] - after[1]

        screen.fill(BG)
        draw_world(screen, g, cam)

        # 顶栏
        pygame.draw.rect(screen, (10, 15, 28), (0, 0, screen.get_width(), 34))
        p = g.player()
        hud = f"{p.name if p else '-'}  ·  回合 {g.turn}  ·  能源 {p.energy:.0f}" if p else ""
        screen.blit(font.render(hud, True, CYAN), (14, 9))
        tip = "拖拽平移 · 滚轮缩放 · ESC 退出"
        tw = font.size(tip)[0]
        screen.blit(font.render(tip, True, DIM), (screen.get_width() - tw - 14, 9))

        # 鼠标所指格子
        mx, my = pygame.mouse.get_pos()
        wx, wy = cam.screen_to_world(mx, my, *screen.get_size())
        q, r = pixel_to_hex(wx, wy)
        t = g.tiles.get((q, r))
        label = f"({q},{r}) " + (t.kind if t else "越界")
        screen.blit(font.render(label, True, DIM), (14, screen.get_height() - 24))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":  # pragma: no cover
    from ..core.demo import make_demo_game

    raise SystemExit(run(make_demo_game()))

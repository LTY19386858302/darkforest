# 黑暗森林 · Python 复刻（骨架）

> 这是 **第 0 周（M0）的交付物**：一个能跑的空壳 + 冻结的接口 + 构建配置。
> 六个人从这份骨架分头开工，不再互相等。
> 通俗版方案见 `darkforest-python-plan-通俗版/`（Markdown + Word 两套）。

---

## 一分钟跑起来

```bash
# 零依赖自检（不需要 pygame / requests）
python -m darkforest --smoke

# 单测（同样零依赖，用 unittest）
python -m unittest discover -s tests -v

# 图形界面（需要先装 pygame-ce）
pip install pygame-ce
python -m darkforest --demo
```

`--smoke` 的输出长这样：

```
darkforest 0.0.1 · smoke
----------------------------------------------------------
  [ok  ] demo 世界已构造  (91 格)
  [ok  ] 格子数符合公式
  ...
----------------------------------------------------------
17/17 项通过
```

---

## 这个骨架包含什么

| 文件 | 作用 | 谁维护 |
|---|---|---|
| `darkforest/core/hex.py` | 六边形坐标、距离、像素互转（**完整实现**） | ② |
| `darkforest/core/state.py` | 5 个 dataclass（**契约，字段已冻结**） | ② |
| `darkforest/core/rules.py` | 地图/行星/恒星/单位四张常量表 | ②③ |
| `darkforest/core/events.py` | 事件对象与收集器（**完整实现**） | ① |
| `darkforest/core/api.py` | 规则层唯一门面（30 个占位函数） | ① |
| `darkforest/core/demo.py` | 手搓迷你世界，给 ⑤ 画图、给 CI 跑 | ① |
| `darkforest/ui/app.py` | pygame 最小客户端：网格 + 相机 | ⑤ |
| `darkforest/ai/` `net/` `server/` `tools/` | 四个空包，占好位置，标明负责人 | ④⑥ |
| `darkforest/__main__.py` | CLI：`--smoke` / `--demo` / `--headless` | ① |
| `tests/` | 4 个测试文件（unittest，零依赖） | 全员 |
| `build.spec` | PyInstaller 打包配置 | ① |
| `.github/workflows/ci.yml` | CI 流水线 | ① |

---

## 三条架构铁律

1. **`core/` 与 `ai/` 不许 import pygame。**
   规则层必须能在无显示器环境跑（CI、服务端、平衡模拟）。
   检查方式：`grep -r "import pygame" darkforest/core darkforest/ai` 必须为空。

2. **规则层只 `return [GameEvent]`，不碰 UI。**
   不许 `toast()`、不许 `render()`、不许改全局变量。

3. **所有人只从 `darkforest.core.api` import。**
   不许直接 import `economy` / `combat` 这些实现模块，否则 ③ 重写内部时会波及全队。

---

## 第 0 周的活儿：① 的 checklist

半天到一天能全做完。

- [x] 建包、`pyproject.toml`、CLI 入口
- [x] `api.py` 30 个签名占位（带 owner 标记）
- [x] `events.py` 事件总线
- [x] `state.py` 五个 dataclass
- [x] `hex.py`（几何是刚需，先给全）
- [x] `demo.py` 迷你世界
- [x] `ui/app.py` 网格 + 相机 demo
- [x] 4 个测试文件 + `--smoke`
- [x] `build.spec` + CI
- [ ] **评审会**：6 个人逐一确认 `api.py` 的签名
- [ ] 打 tag `v0-contract`
- [ ] 把方案文档里的接口表同步成"已冻结"

### 评审会上要逐条确认的 8 个签名

```python
start_game(size_key, ai_strength, pace, *, seed) -> Game
next_turn(g, *, player_id) -> list[GameEvent]
civ_income(g, c) -> Income
ai_turn(g, c, *, player_id) -> list[GameEvent]
snapshot_for(g, slot) -> dict
power(u) -> float
reach_map(g, u) -> set[Coord]
to_json(g) -> dict
```

> 只要这 8 个没争议，剩下 22 个都是它们的变体，不会卡住并行开发。

---

## 怎么验证骨架是合格的

四条硬标准，缺一条就说明契约还没冻结：

1. `python -m darkforest --smoke` 退出码 0，且打印 `N/N 项通过`
2. `python -m unittest discover -s tests` 全绿（当前 30 个用例）
3. `grep -rn "import pygame" darkforest/core` 无输出
4. `python -m darkforest --demo` 能弹出窗口，拖拽/滚轮正常（装了 pygame 的前提下）

---

## 各人的下一步

| 角色 | 从哪开始 |
|---|---|
| ② | 实现 `worldgen.start_game`，把 `--headless` 里的 `[skip]` 打掉 |
| ③ | 从 `civ_income` 开始，第一个黄金基线测试就写它 |
| ④ | 先写 `tools/balance.py`（能无头跑一局），再写 AI |
| ⑤ | 把 `ui/app.py` 拆成 `camera.py` + `render_world.py`，加静态层缓存 |
| ⑥ | 先做 `server/relay.py`（不依赖别人），再做客户端 |

---

## 打包

```bash
pip install -e ".[dev]"
pyinstaller build.spec
# 产物：dist/darkforest/darkforest.exe
```

注意：`build.spec` 里的 `datas` 必须包含字体和图标，否则 exe 里找不到资源。

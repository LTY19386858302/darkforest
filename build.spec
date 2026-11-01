# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 配置。

    pyinstaller build.spec

产物：dist/darkforest/darkforest.exe（目录模式，启动快）
若想单文件，把 EXE(... exclude_binaries=False) 并去掉 COLLECT。

三个必须注意的点：
1. 字体/图标必须写进 datas，否则 exe 里找不到（docs/06 第 9.3 节）；
2. --windowed 之后 print 会消失，日志必须写文件；
3. 首次启动会解压，要有启动提示。
"""

from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH)  # noqa: F821  (PyInstaller 注入)
ASSETS = ROOT / "darkforest" / "assets"

datas = []
# 资源目录可能还没建，存在才打包，避免第 0 周就报错
for pattern, dest in (("*", "darkforest/assets/fonts"),):
    for path in (ASSETS / "fonts").glob(pattern) if (ASSETS / "fonts").exists() else []:
        datas.append((str(path), dest))
for path in (ASSETS / "icons").glob("*") if (ASSETS / "icons").exists() else []:
    datas.append((str(path), "darkforest/assets/icons"))

a = Analysis(  # noqa: F821
    [str(ROOT / "darkforest" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=["pygame", "requests"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["numpy", "pandas", "matplotlib", "tkinter"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="darkforest",
    debug=False,
    strip=False,
    upx=False,
    console=False,          # 无控制台窗口；日志走文件
    icon=None,              # 有图标后填 str(ASSETS / "icons" / "app.ico")
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="darkforest",
)

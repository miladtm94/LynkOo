# PyInstaller spec for the LynkOo standalone desktop app.
# Build with: .venv/bin/pyinstaller desktop.spec --noconfirm
from PyInstaller.utils.hooks import collect_all

datas = [("app/frontend/dist", "app/frontend/dist")]
binaries = []
hiddenimports = []

# These packages load data files (dictionaries, locales, cert bundles) at
# runtime via importlib.resources, which PyInstaller's default analysis
# doesn't pick up automatically.
for pkg in ("pykakasi", "ytmusicapi", "certifi"):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

hiddenimports += [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
]

a = Analysis(
    ["app/desktop.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LynkOo",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="LynkOo",
)

app = BUNDLE(
    coll,
    name="LynkOo.app",
    icon=None,
    bundle_identifier="com.lynkoo.desktop",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": "0.1.0",
    },
)

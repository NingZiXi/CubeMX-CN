"""Build the Windows launcher with the current Python environment's PyInstaller."""
from pathlib import Path
import shutil
import subprocess
import sys
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist/CubeMX-CN"

if __name__ == "__main__":
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("VERSION must contain a numeric major.minor.patch version")
    for filename in ("cubemx-cn-agent.jar", "cubemx-cn-bootstrap.jar"):
        if not (DEST / filename).is_file():
            raise SystemExit("Run python tools/build.py before packaging")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
                    "--name", "CubeMX-CN", "--distpath", str(DEST),
                    "--workpath", str(ROOT / "build/pyinstaller"), str(ROOT / "launcher.py")], cwd=ROOT, check=True)
    shutil.copy2(ROOT / "README.md", DEST / "使用说明.md")
    shutil.copy2(ROOT / "translations/zh_CN.tsv", DEST / "translations/zh_CN.tsv")
    package = ROOT / f"dist/CubeMX-CN-v{version}-windows-x64.zip"
    # Explicit inclusion list prevents local logs, old artifacts, or ST packages from shipping.
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename in ("CubeMX-CN.exe", "cubemx-cn-agent.jar", "cubemx-cn-bootstrap.jar",
                         "translations/zh_CN.tsv", "使用说明.md"):
            archive.write(DEST / filename, f"CubeMX-CN/{filename}")
        for filename in ("CHANGELOG.md", "CONTRIBUTING.md", "docs/architecture.md", "docs/verification.md", "docs/images/home.png"):
            archive.write(ROOT / filename, f"CubeMX-CN/{filename}")
    with package.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    package.with_suffix(".sha256").write_text(f"{digest}  {package.name}\n", encoding="ascii")
    print(DEST / "CubeMX-CN.exe")

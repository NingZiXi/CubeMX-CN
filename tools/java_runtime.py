"""Locate a Java 21 JDK without depending on a developer's installation path."""
from pathlib import Path
import os
import re
import shutil


def resolve_jdk(explicit: Path | None = None) -> Path:
    candidates = []
    if explicit is not None:
        candidates.append(explicit)
    else:
        if os.environ.get("JAVA_HOME"):
            candidates.append(Path(os.environ["JAVA_HOME"]))
        javac = shutil.which("javac")
        if javac:
            candidates.append(Path(javac).resolve().parent.parent)
    for candidate in candidates:
        candidate = candidate.expanduser().resolve()
        if not all((candidate / "bin" / name).is_file() for name in ("java.exe", "javac.exe")):
            continue
        try:
            release = (candidate / "release").read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r'^JAVA_VERSION="21(?:\.|\+|")', release, re.M):
            return candidate
    raise SystemExit("找不到 Windows JDK 21。请设置 JAVA_HOME，或使用 --jdk 指定包含 bin/javac.exe 的目录。")

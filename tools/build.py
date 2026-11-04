"""Reproducible JDK-only agent build. No third-party Java dependencies."""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import zipfile
from java_runtime import resolve_jdk

ROOT = pathlib.Path(__file__).resolve().parents[1]


def build(jdk: pathlib.Path, output: pathlib.Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    classes = ROOT / "build" / "classes"
    bootstrap = ROOT / "build" / "bootstrap"
    # Keep outputs separate; javac overwrites known classes, no recursive deletion.
    for source, destination, extra in (
        (ROOT / "agent/bootstrap", bootstrap, []),
        (ROOT / "agent/src", classes, ["--add-exports", "java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED"]),
    ):
        destination.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(jdk / "bin/javac.exe"), "-encoding", "UTF-8", "-source", "17", "-target", "17",
                        *extra, "-d", str(destination), *map(str, sorted(source.rglob("*.java")))], check=True)
    manifest = ("Manifest-Version: 1.0\nPremain-Class: cubemx.cn.Agent\n"
                "Can-Retransform-Classes: true\n\n")
    for directory, filename, main in (
        (bootstrap, "cubemx-cn-bootstrap.jar", "Manifest-Version: 1.0\n\n"),
        (classes, "cubemx-cn-agent.jar", manifest),
    ):
        with zipfile.ZipFile(output / filename, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("META-INF/MANIFEST.MF", main)
            for path in sorted(directory.rglob("*.class")):
                archive.write(path, path.relative_to(directory).as_posix())
    translations = output / "translations"
    translations.mkdir(exist_ok=True)
    if (ROOT / "translations/zh_CN.tsv").is_file():
        shutil.copy2(ROOT / "translations/zh_CN.tsv", translations / "zh_CN.tsv")
    print(f"Built agent: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jdk", type=pathlib.Path, help="JDK 21 directory; defaults to JAVA_HOME or PATH")
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "dist/CubeMX-CN")
    args = parser.parse_args()
    build(resolve_jdk(args.jdk), args.output.resolve())

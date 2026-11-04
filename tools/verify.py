"""Launcher unit tests and real Java/Swing rendering tests, including Unicode paths."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys
from java_runtime import resolve_jdk

ROOT = Path(__file__).resolve().parents[1]


def run(jdk: Path):
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    bundle = ROOT / "dist/CubeMX-CN"
    classes = ROOT / "build/test-classes"
    classes.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(jdk / "bin/javac.exe"), "-encoding", "UTF-8", "-cp",
                    str(bundle / "cubemx-cn-bootstrap.jar"), "-d", str(classes),
                    str(ROOT / "tests/RenderSmoke.java")], check=True)
    for directory, name in ((bundle, "render-smoke.png"), (ROOT / "build/汉化 测试路径", "render-unicode-path.png")):
        if directory != bundle:
            (directory / "translations").mkdir(parents=True, exist_ok=True)
            for filename in ("cubemx-cn-agent.jar", "cubemx-cn-bootstrap.jar", "translations/zh_CN.tsv"):
                shutil.copy2(bundle / filename, directory / filename)
        subprocess.run([str(jdk / "bin/java.exe"), f"-javaagent:{directory / 'cubemx-cn-agent.jar'}",
                        f"-Dcubemx.cn.dictionary={directory / 'translations/zh_CN.tsv'}",
                        "-cp", str(classes), "RenderSmoke", str(ROOT / "reports" / name)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jdk", type=Path, help="JDK 21 directory; defaults to JAVA_HOME or PATH")
    run(resolve_jdk(parser.parse_args().jdk))

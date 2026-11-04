"""Launcher unit tests and real Java/Swing rendering tests, including Unicode paths."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys
import tempfile
from java_runtime import resolve_jdk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from windows_paths import jvm_path


def run(jdk: Path):
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    bundle = ROOT / "dist/CubeMX-CN"
    classes = ROOT / "build/test-classes"
    classes.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(jdk / "bin/javac.exe"), "-encoding", "UTF-8", "-cp",
                    str(bundle / "cubemx-cn-bootstrap.jar"), "-d", str(classes),
                    str(ROOT / "tests/RenderSmoke.java")], check=True)
    # Use the Windows temp volume, which normally provides 8.3 aliases, instead
    # of assuming that the source checkout's volume supports native Unicode paths.
    with tempfile.TemporaryDirectory(prefix="CubeMX 汉化 测试 ") as temporary:
        for directory, name in ((bundle, "render-smoke.png"), (Path(temporary), "render-unicode-path.png")):
            if directory != bundle:
                (directory / "translations").mkdir(parents=True, exist_ok=True)
                for filename in ("cubemx-cn-agent.jar", "cubemx-cn-bootstrap.jar", "translations/zh_CN.tsv"):
                    shutil.copy2(bundle / filename, directory / filename)
            subprocess.run([str(jdk / "bin/java.exe"), f"-javaagent:{jvm_path(directory / 'cubemx-cn-agent.jar')}",
                            f"-Dcubemx.cn.dictionary={jvm_path(directory / 'translations/zh_CN.tsv')}",
                            "-cp", str(classes), "RenderSmoke", str(ROOT / "reports" / name)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jdk", type=Path, help="JDK 21 directory; defaults to JAVA_HOME or PATH")
    run(resolve_jdk(parser.parse_args().jdk))

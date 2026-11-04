import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.java_runtime import resolve_jdk


class JdkDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="CubeMX JDK 测试 ")
        self.addCleanup(self.temp.cleanup)
        self.jdk = Path(self.temp.name)
        (self.jdk / "bin").mkdir()
        for name in ("java.exe", "javac.exe"):
            (self.jdk / "bin" / name).write_bytes(b"fixture")
        (self.jdk / "release").write_text('JAVA_VERSION="21.0.10"', encoding="utf-8")

    def test_explicit_jdk(self):
        self.assertEqual(resolve_jdk(self.jdk), self.jdk.resolve())

    def test_java_home(self):
        with patch.dict(os.environ, {"JAVA_HOME": str(self.jdk)}):
            self.assertEqual(resolve_jdk(), self.jdk.resolve())

    def test_invalid_explicit_does_not_fall_back(self):
        (self.jdk / "release").write_text('JAVA_VERSION="17.0.1"', encoding="utf-8")
        with self.assertRaises(SystemExit):
            resolve_jdk(self.jdk)

    def test_jre_without_compiler_is_rejected(self):
        (self.jdk / "bin/javac.exe").unlink()
        with self.assertRaises(SystemExit):
            resolve_jdk(self.jdk)


if __name__ == "__main__":
    unittest.main()

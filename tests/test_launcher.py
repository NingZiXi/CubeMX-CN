import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile
import launcher


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="CubeMX 中文 测试 ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.install = self.root / "原版 STM32CubeMX"
        (self.install / "jre/bin").mkdir(parents=True)
        (self.install / "jre/bin/java.exe").write_bytes(b"test fixture")
        (self.install / "jre/release").write_text('JAVA_VERSION="21.0.10"', encoding="utf-8")
        with zipfile.ZipFile(self.install / "STM32CubeMX.exe", "w") as z:
            z.writestr("META-INF/MANIFEST.MF", f"Main-Class: {launcher.MAIN_CLASS}\n")
            z.writestr("META-INF/maven/com.st.microxplorer/mcu/pom.properties", "version=6.18.1-RC2\n")
        (self.install / "STM32CubeMX.l4j.ini").write_text(
            "# test\n-Dfile.encoding=UTF8\n--add-opens java.desktop/java.awt=ALL-UNNAMED\n", encoding="utf-8")
        self.bundle = self.root / "汉化包"
        (self.bundle / "translations").mkdir(parents=True)
        for name in ("cubemx-cn-agent.jar", "cubemx-cn-bootstrap.jar"):
            (self.bundle / name).write_bytes(b"jar fixture")
        self.dictionary = self.bundle / "translations/zh_CN.tsv"
        self.dictionary.write_text("File\t文件\nSave\t保存\n", encoding="utf-8")
        self.addCleanup(patch.stopall)
        patch.object(launcher, "BUNDLE", self.bundle).start()
        patch.object(launcher, "STATE", self.root / "state").start()

    def test_inspection_and_runtime_gate(self):
        info = launcher.inspect_install(self.install)
        self.assertEqual(info["component_version"], "6.18.1-RC2")
        (self.install / "jre/release").write_text('JAVA_VERSION="17.0.1"', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Java 21"):
            launcher.inspect_install(self.install)

    def test_missing_and_non_cubemx_install(self):
        with self.assertRaises(ValueError):
            launcher.inspect_install(self.root)
        (self.install / "STM32CubeMX.exe").write_bytes(b"not a Java package")
        with self.assertRaises(ValueError):
            launcher.inspect_install(self.install)

    def test_dictionary_rejects_conflicts_and_invalid_lines(self):
        self.assertEqual(launcher.validate_dictionary(self.dictionary), 2)
        for text in ("", "File", "File\t文件\textra", "File\t文件\nFile\t档案"):
            self.dictionary.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                launcher.validate_dictionary(self.dictionary)

    def test_launch_uses_argument_list_and_keeps_installation_unchanged(self):
        before = {p.relative_to(self.install): p.read_bytes() for p in self.install.rglob("*") if p.is_file()}
        fake = Mock(pid=123)
        with patch.object(launcher.subprocess, "Popen", return_value=fake) as popen:
            process, log, info = launcher.launch(self.install)
        self.assertIs(process, fake)
        args, kwargs = popen.call_args
        self.assertIsInstance(args[0], list)
        runtime, dictionary = launcher.prepare_agent(self.bundle, self.dictionary)
        self.assertIn(f"-javaagent:{launcher.jvm_path(runtime / 'cubemx-cn-agent.jar')}", args[0])
        # Windows runners can expose TEMP through an 8.3 alias (RUNNER~1).
        # The launcher deliberately resolves the dictionary to its canonical path.
        self.assertIn(f"-Dcubemx.cn.dictionary={launcher.jvm_path(dictionary)}", args[0])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["cwd"], self.install.resolve())
        self.assertEqual(json.loads(log.with_suffix(".json").read_text(encoding="utf-8"))["pid"], 123)
        after = {p.relative_to(self.install): p.read_bytes() for p in self.install.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_english_has_no_agent(self):
        with patch.object(launcher.subprocess, "Popen", return_value=Mock(pid=123)) as popen:
            launcher.launch(self.install, chinese=False)
        self.assertFalse(any("javaagent" in s or "cubemx.cn" in s for s in popen.call_args.args[0]))

    def test_invalid_dictionary_cannot_launch(self):
        self.dictionary.write_text("broken", encoding="utf-8")
        with patch.object(launcher.subprocess, "Popen") as popen:
            with self.assertRaises(ValueError):
                launcher.launch(self.install)
            popen.assert_not_called()

    def test_post_launch_metadata_failure_still_returns_process(self):
        original_write = Path.write_text
        count = 0
        def write(path, *args, **kwargs):
            nonlocal count
            if path.suffix == ".json" and path.parent.name == "logs":
                count += 1
                if count == 2:
                    raise OSError("disk full after launch")
            return original_write(path, *args, **kwargs)
        fake = Mock(pid=123)
        with patch.object(Path, "write_text", write), patch.object(launcher.subprocess, "Popen", return_value=fake):
            process, _, _ = launcher.launch(self.install)
        self.assertIs(process, fake)

    def test_readiness_is_not_claimed_after_process_exit(self):
        log = self.root / "test.log"
        log.write_text("[CubeMX-CN] READY", encoding="utf-8")
        process = Mock(returncode=1)
        process.poll.return_value = 1
        with self.assertRaises(RuntimeError):
            launcher.wait_ready(process, log)


if __name__ == "__main__":
    unittest.main()

"""Paths accepted by the Windows JVM's native agent loader on non-Chinese systems."""
from pathlib import Path
import ctypes
import os
import hashlib
import tempfile


def jvm_path(path: Path) -> str:
    path = path.resolve()
    if os.name != "nt":
        return str(path)
    # Agent_OnLoad uses the Windows ANSI code page in some JDK 21 builds.
    # A filesystem-provided 8.3 alias avoids lossy conversion of Chinese paths.
    function = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
    function.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
    function.restype = ctypes.c_uint32
    size = function(str(path), None, 0)
    value = str(path)
    if size:
        buffer = ctypes.create_unicode_buffer(size)
        written = function(str(path), buffer, size)
        if 0 < written < size:
            value = buffer.value
    try:
        value.encode("mbcs", errors="strict")
    except UnicodeEncodeError as error:
        raise ValueError("当前 Java 无法读取此路径，且文件系统未提供短路径别名。请将汉化包移到纯英文路径后重试。") from error
    return value


def prepare_agent(bundle: Path, dictionary: Path) -> tuple[Path, Path]:
    """Stage Unicode paths into a content-addressed ASCII temp cache.

    Some JDKs canonicalize 8.3 aliases back to Unicode inside the native loader,
    so aliases alone do not reliably solve the problem on English Windows.
    """
    source = bundle.resolve()
    dictionary = dictionary.resolve()
    if str(source).isascii() and str(dictionary).isascii():
        return source, dictionary
    files = {name: (source / name).read_bytes() for name in
             ("cubemx-cn-agent.jar", "cubemx-cn-bootstrap.jar")}
    files["zh_CN.tsv"] = dictionary.read_bytes()
    digest = hashlib.sha256()
    for name, data in sorted(files.items()):
        digest.update(name.encode("ascii"))
        digest.update(hashlib.sha256(data).digest())
    destination = Path(tempfile.gettempdir()).resolve() / "CubeMX-CN" / "runtime" / digest.hexdigest()
    if not str(destination).isascii():
        raise ValueError("Java 原生加载器不兼容当前中文路径。请把汉化包与词库移动到纯英文路径后重试。")
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = destination / name
        if target.is_file() and target.read_bytes() == data:
            continue
        with tempfile.NamedTemporaryFile(dir=destination, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
        try:
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    return destination, destination / "zh_CN.tsv"

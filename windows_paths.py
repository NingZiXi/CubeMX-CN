"""Paths accepted by the Windows JVM's native agent loader on non-Chinese systems."""
from pathlib import Path
import ctypes
import os


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

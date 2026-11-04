"""Inventory CONSTANT_String literals from ST Java classes, without executing them.

Usage: python tools/extract_strings.py D:/STM32CubeMX --output reports/strings.json
Only the main executable ZIP and plugins/**/*.jar are read. The output records
archive/class provenance; a literal's presence does not establish UI execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile


def class_strings(data: bytes) -> list[str]:
    if data[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("Not a Java class")
    count = struct.unpack_from(">H", data, 8)[0]
    values: dict[int, str] = {}
    refs: list[int] = []
    pos, index = 10, 1
    sizes = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 9: 4, 10: 4, 11: 4,
             12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
    while index < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            length = struct.unpack_from(">H", data, pos)[0]
            pos += 2
            # Java modified UTF-8 uses C0 80 for NUL and encoded surrogate pairs.
            raw = data[pos:pos + length].replace(b"\xc0\x80", b"\0")
            value = raw.decode("utf-8", "surrogatepass")
            values[index] = value.encode("utf-16", "surrogatepass").decode("utf-16")
            pos += length
        elif tag == 8:
            refs.append(struct.unpack_from(">H", data, pos)[0])
            pos += 2
        elif tag in sizes:
            pos += sizes[tag]
            if tag in (5, 6):
                index += 1
        else:
            raise ValueError(f"Unknown constant-pool tag {tag}")
        index += 1
    return [values[ref] for ref in refs]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("installation", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/strings.json"))
    args = parser.parse_args()
    root = args.installation.resolve()
    archives = [root / "STM32CubeMX.exe", *sorted((root / "plugins").rglob("*.jar"))]
    literals: dict[str, list[str]] = {}
    inventory, errors = [], []
    for archive in archives:
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        rel = archive.relative_to(root).as_posix()
        classes = 0
        with zipfile.ZipFile(archive) as package:
            for name in package.namelist():
                if not (name.endswith(".class") and name.startswith(("com/st/", "st/"))):
                    continue
                classes += 1
                try:
                    values = class_strings(package.read(name))
                except (ValueError, IndexError, struct.error, UnicodeError) as exc:
                    errors.append({"source": f"{rel}!{name}", "error": str(exc)})
                    continue
                for value in values:
                    if value.strip() and re.search("[A-Za-z]", value):
                        literals.setdefault(value, []).append(f"{rel}!{name}")
        inventory.append({"archive": rel, "sha256": digest, "classes": classes})
    result = {"installation": str(root), "archives": inventory, "errors": errors,
              "strings": [{"text": text, "sources": sorted(set(sources))}
                          for text, sources in sorted(literals.items())]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"archives": len(inventory), "strings": len(literals),
                      "errors": len(errors), "output": str(args.output)}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

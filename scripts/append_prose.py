"""manual_prose.py의 MANUAL dict에 항목 추가."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "manual_prose.py"


def append(folio_id: str, prose: str) -> None:
    text = TARGET.read_text(encoding="utf-8")
    # MANUAL dict 찾기
    marker = "MANUAL: dict[str, str] = {}"
    if marker in text:
        # 빈 dict → 첫 항목 추가
        new = f'MANUAL: dict[str, str] = {{\n    "{folio_id}": (\n        "{prose}"\n    ),\n}}'
        text = text.replace(marker, new)
    else:
        # 닫는 } 앞에 삽입
        idx = text.rfind("}")
        prose_esc = prose.replace('"', '\\"')
        insertion = f'    "{folio_id}": (\n        "{prose_esc}"\n    ),\n'
        text = text[:idx] + insertion + text[idx:]
    TARGET.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        append(sys.argv[1], sys.argv[2])
        print(f"appended {sys.argv[1]}")

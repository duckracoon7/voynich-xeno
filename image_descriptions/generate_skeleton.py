#!/usr/bin/env python3
"""
폴리오 이미지 설명 스켈레톤 생성기.

사용:
    python generate_skeleton.py f2v
    python generate_skeleton.py f1r f1v f2r f2v ...

RF1b-e.txt에서 EVA 텍스트와 IVTFF 메타데이터를 추출해
image_descriptions/<section>/<folio>.md 스켈레톤을 생성한다.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "RF1b-e.txt"
OUT_ROOT = ROOT / "image_descriptions"

# IVTFF $I 코드 → 섹션
ILLUSTRATION_TO_SECTION = {
    "T": "text",
    "H": "herbal",
    "A": "astronomical",
    "Z": "zodiac",
    "B": "biological",
    "C": "cosmological",
    "P": "pharmaceutical",
    "S": "recipes",
}

# IVTFF locator → 사람이 읽을 라벨
LOCATOR_DESC = {
    "@P0": "본문 단락 시작",
    "+P0": "본문 단락 연속",
    "*P0": "새 단락 시작",
    "=Pt": "제목",
    "@Pb": "이미지 부속 텍스트",
    "+Pb": "이미지 부속 연속",
    "@Lp": "식물 라벨",
    "@Lc": "용기 라벨 (pharmaceutical)",
    "@Lf": "식물 단편 라벨 (pharmaceutical)",
    "@Ls": "별 라벨 (astronomical/recipes)",
    "@Lz": "황도궁 인물 라벨 (zodiac)",
    "&Lz": "황도궁 인물 라벨 연속",
    "@Cc": "원형 텍스트 (zodiac)",
    "@L0": "기타 라벨",
}


def parse_header(line: str) -> dict:
    """헤더 라인의 $X=Y 메타데이터 추출."""
    meta = {}
    for m in re.finditer(r"\$([A-Z])=(\S+?)(?:[ >]|$)", line):
        meta[m.group(1)] = m.group(2).rstrip(">")
    return meta


def extract_folio(folio_id: str) -> tuple[str, dict, list[tuple[str, str, str]]]:
    """RF1b-e.txt에서 한 폴리오의 헤더와 라인들을 추출."""
    text = DATA_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    header_line = None
    body: list[tuple[str, str, str]] = []  # (line_id, locator, eva_text)

    in_folio = False
    for line in lines:
        if line.startswith(f"<{folio_id}>") and not line.startswith(f"<{folio_id}."):
            header_line = line
            in_folio = True
            continue
        if in_folio:
            # 다음 폴리오 헤더 만나면 종료
            m_next = re.match(r"<(f\d+[rv]\d*)>", line)
            if m_next and m_next.group(1) != folio_id:
                break
            m = re.match(rf"<{re.escape(folio_id)}\.(\d+),([^>]+)>\s+(.*)", line)
            if m:
                body.append((m.group(1), m.group(2), m.group(3).strip()))
    if header_line is None:
        raise SystemExit(f"폴리오 {folio_id}을(를) {DATA_FILE}에서 찾을 수 없음")
    return header_line, parse_header(header_line), body


def section_of(meta: dict) -> str:
    return ILLUSTRATION_TO_SECTION.get(meta.get("I", ""), "unknown")


def render(folio_id: str, header: str, meta: dict, body: list) -> str:
    section = section_of(meta)
    n_labels = sum(1 for _, loc, _ in body if loc.startswith(("@L", "&L")))
    n_paragraphs = sum(1 for _, loc, _ in body if loc in ("@P0", "*P0"))

    # 라인 표
    rows = []
    for lid, loc, eva in body:
        desc = LOCATOR_DESC.get(loc, loc)
        rows.append(f"| f{folio_id[1:]}.{lid} | `{loc}` | {desc} | `{eva}` |")
    line_table = "\n".join(rows)

    return f"""---
folio_id: {folio_id}
section: {section}
currier_lang: {meta.get("L", "?")}
scribe: {meta.get("H", "?")}
illustration_type: {meta.get("I", "?")}
quire: {meta.get("Q", "?")}
foldout: false
beinecke_url: https://collections.library.yale.edu/catalog/2002046
inspected_date: 2026-__-__
inspector: ___
---

# {folio_id} — {section} 섹션

> 자동 생성된 스켈레톤. 이미지를 보고 §1~§3, §6의 빈 항목을 채울 것.

## 자동 메타데이터

```
{header}
```

- 라인 수: {len(body)}
- 단락 시작 (@P0/*P0) 수: {n_paragraphs}
- 라벨 (@L*/&L*) 수: {n_labels}

## EVA 라인 일람

| 라인 ID | locator | 종류 | EVA |
|---------|---------|------|-----|
{line_table}

## 1. 페이지 전체 구성 *(이미지 보고 작성)*

- 레이아웃 방향:
- 이미지 영역 비율:
- 텍스트 블록 개수:
- 이미지와 텍스트의 배치 관계:

## 2. 색상 팔레트 *(이미지 보고 작성)*

| 색 | 사용된 영역 |
|----|-------------|
| | |

## 3. 이미지 객체 인벤토리 *(이미지 보고 작성)*

### 객체 1
- 위치:
- 크기:
- 형태:

## 4. 라벨-객체 매핑 표

(라벨 수 {n_labels}개. 위 라인 일람의 `@L*` 항목과 1:1로 짝지을 것)

| 라인 ID | EVA 라벨 | 객체 위치 | 객체 형태 |
|---------|----------|-----------|-----------|
| | | | |

## 6. 특이 관찰 *(이미지 보고 작성)*

-

## 7. 정량 요약

```yaml
n_text_blocks: {n_paragraphs}
n_distinct_objects: ___
n_labels: {n_labels}
n_colors_used: ___
has_circular_structure: false
has_radial_symmetry: false
has_human_figure: false
has_container: false
```
"""


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for folio_id in sys.argv[1:]:
        try:
            header, meta, body = extract_folio(folio_id)
        except SystemExit as e:
            print(e, file=sys.stderr)
            continue
        section = section_of(meta)
        out_dir = OUT_ROOT / section
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{folio_id}.md"
        out_file.write_text(render(folio_id, header, meta, body), encoding="utf-8")
        print(f"  wrote {out_file.relative_to(ROOT)}  (lines={len(body)}, labels={sum(1 for _, loc, _ in body if loc.startswith(('@L', '&L')))})")


if __name__ == "__main__":
    main()

"""
Phase 15 — manual_prose.py를 우선 적용하는 책 어셈블러 (v2).
"""
from __future__ import annotations
import re
import random
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
DIC = ROOT / "artifacts" / "dictionary"
IMG = ROOT / "image_descriptions"

sys.path.insert(0, str(Path(__file__).parent))
from phase14_book import (
    parse_yaml, SECTION_TITLE, ANCHOR_NOUN, folio_anchors,
    prose_herbal, prose_astronomical, prose_cosmological, prose_zodiac,
    prose_biological, prose_pharmaceutical, prose_recipes, prose_text,
    folio_sort_key, PREFACE,
)
from manual_prose import MANUAL

SECTION_FN = {
    "herbal": prose_herbal,
    "astronomical": prose_astronomical,
    "cosmological": prose_cosmological,
    "zodiac": prose_zodiac,
    "biological": prose_biological,
    "pharmaceutical": prose_pharmaceutical,
    "recipes": prose_recipes,
    "text": prose_text,
}


def main() -> int:
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")
    corpus = pd.read_parquet(COR / "corpus.parquet")
    pmi_df = pd.read_parquet(DIC / "token_feature_pmi.parquet")

    folio_meta = folio_meta.assign(
        sort_key=folio_meta["folio_id"].apply(folio_sort_key)
    ).sort_values("sort_key").reset_index(drop=True)

    rng = random.Random(42)
    out: list[str] = [PREFACE]
    sections_seen: set[str] = set()

    f1r = folio_meta[folio_meta["folio_id"] == "f1r"]
    if not f1r.empty:
        frow = f1r.iloc[0]
        section = frow["section"]
        out.append("## 첫 글\n")
        if "f1r" in MANUAL:
            prose = MANUAL["f1r"]
        else:
            md_path = IMG / section / "f1r.md"
            meta = parse_yaml(md_path.read_text(encoding="utf-8")) if md_path.exists() else {}
            anchors = folio_anchors("f1r", corpus, pmi_df)
            prose = SECTION_FN[section](meta, anchors, rng) if section in SECTION_FN else ""
        out.append(f"### f1r\n\n{prose}\n")
        sections_seen.add("text")

    n_manual = 0
    n_auto = 0
    for _, frow in folio_meta.iterrows():
        fid = frow["folio_id"]
        if fid == "f1r":
            continue
        section = frow["section"]
        if section not in SECTION_TITLE:
            continue

        if section not in sections_seen:
            out.append(f"\n## {SECTION_TITLE[section]}\n")
            sections_seen.add(section)

        if fid in MANUAL:
            prose = MANUAL[fid]
            n_manual += 1
        else:
            md_path = IMG / section / f"{fid}.md"
            meta = parse_yaml(md_path.read_text(encoding="utf-8")) if md_path.exists() else {}
            anchors = folio_anchors(fid, corpus, pmi_df)
            try:
                prose = SECTION_FN[section](meta, anchors, rng)
                n_auto += 1
            except Exception:
                prose = "(이 페이지의 데이터는 빈약하거나 누락되었다.)"

        lang = (frow.get("currier_lang") or "").strip()
        lang_tag = f" · {lang}" if lang in ("A", "B") else ""

        out.append(f"### {fid}{lang_tag}\n\n{prose}\n")

    out.append("""
---

## 후기

이 책은 끝까지 읽혔지만, *번역되었다*고 말할 수는 없다.

각 페이지는 *시각적으로* 분명한 사실을 가지고 있다 — 거기에 한 형상이 있고, 사람이 풀에 들어가 있고, 별이 둘레에 있다. 그 사실을 우리 언어로 적었다. 그러나 *그 페이지의 글*이 무엇을 말하는지는 600년이 지난 지금도 모른다.

우리가 적은 것은 *그 자리에 어떤 글이 적혀 있을 가능성*의 한 갈래다. 우리 사전이 가리키는 *통계적 짝짓기*는 견고하지만 (50/50 페어가 p<0.01에서 유의), 그 짝짓기가 *의미*인지 *우연한 공기성*인지는 데이터만으로 가를 수 없었다.

그러므로 이 책은:
- 보이니치를 *읽고 싶어 하는 욕구*를 위한 한 번의 답이지
- *읽는다*는 행위 자체는 아직 일어나지 않았다.

그 행위가 가능해진다면, 이 책의 모든 페이지는 즉시 *틀린 책*으로 바뀐다.
그리고 그것이, 이 책이 자기 자신에게 바라는 일이다.

---

*작성: 2026-05-04*
*GitHub: https://github.com/duckracoon7/voynich-xeno*
""")

    book = "\n".join(out)
    out_path = ROOT / "artifacts" / "voynich_book.md"
    out_path.write_text(book, encoding="utf-8")
    print(f"✅ Book written: {out_path}")
    print(f"   Manual: {n_manual} pages | Auto: {n_auto} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())

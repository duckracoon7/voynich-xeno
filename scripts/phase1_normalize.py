"""
Phase 1 — 코퍼스 정규화

IVTFF 2.0 EVA 전사본을 분석 가능한 parquet로 변환.

입력: data/RF1b-e.txt
출력:
  artifacts/corpus/corpus.parquet         (전체)
  artifacts/corpus/corpus_A.parquet       (Currier A)
  artifacts/corpus/corpus_B.parquet       (Currier B)
  artifacts/corpus/folio_meta.parquet     (폴리오별 메타데이터)
  artifacts/corpus/tokens.parquet         (토큰 단위 분해)

스키마 (corpus.parquet):
  folio_id, line_id, locator, eva_text,
  section, currier_lang, scribe, quire, illustration_type, foldout
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "RF1b-e.txt"
OUT = ROOT / "artifacts" / "corpus"
OUT.mkdir(parents=True, exist_ok=True)

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


def parse_header_meta(line: str) -> dict[str, str]:
    """폴리오 헤더의 $X=Y 메타데이터 추출."""
    return dict(re.findall(r"\$([A-Z])=(\S+?)(?:[ >]|$)", line))


def parse_ivtff(text: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """IVTFF 텍스트 → (corpus_df, folio_meta_df)."""
    lines = text.splitlines()
    corpus_rows: list[dict] = []
    folio_rows: list[dict] = []

    current_folio = None
    current_meta: dict[str, str] = {}

    for raw in lines:
        if not raw.strip() or raw.startswith("#"):
            continue

        # 폴리오 헤더: <fNNr> [<! $Q=A ...>]
        m_folio = re.match(r"<(f\d+[rv]\d?)>\s*(?:<!\s*(.*?)\s*>)?", raw)
        if m_folio:
            current_folio = m_folio.group(1)
            current_meta = parse_header_meta(m_folio.group(2) or "")
            illust = current_meta.get("I", "")
            folio_rows.append({
                "folio_id": current_folio,
                "section": ILLUSTRATION_TO_SECTION.get(illust, "unknown"),
                "currier_lang": current_meta.get("L", ""),
                "scribe": current_meta.get("H", ""),
                "quire": current_meta.get("Q", ""),
                "illustration_type": illust,
                "page_seq": current_meta.get("B", ""),
                "x_marker": current_meta.get("X", ""),
            })
            continue

        # 라인: <fNNr.LL,LOCATOR>     EVA_TEXT
        m_line = re.match(r"<(f\d+[rv]\d?)\.(\d+),([^>]+)>\s*(.*)", raw)
        if m_line:
            folio_id, line_no, locator, eva = m_line.groups()
            corpus_rows.append({
                "folio_id": folio_id,
                "line_id": int(line_no),
                "locator": locator,
                "eva_text": eva.strip(),
                "section": ILLUSTRATION_TO_SECTION.get(current_meta.get("I", ""), "unknown"),
                "currier_lang": current_meta.get("L", ""),
                "scribe": current_meta.get("H", ""),
                "quire": current_meta.get("Q", ""),
                "illustration_type": current_meta.get("I", ""),
                "foldout": _is_foldout(folio_id),
            })

    return pd.DataFrame(corpus_rows), pd.DataFrame(folio_rows)


def _is_foldout(folio_id: str) -> bool:
    """폴리오 ID가 sub-page인지 (예: f67r1, f72v3)."""
    return bool(re.match(r"f\d+[rv]\d", folio_id))


# 토큰 분리 — EVA의 단어 구분자
WORD_SEP = re.compile(r"[.,]+|<->")
GLYPH_GROUP = re.compile(r"\{[^}]+\}|@\d+;|[a-zA-Z']")


def tokenize_eva(eva: str) -> list[str]:
    """EVA 텍스트를 단어 단위로 분리.

    - `.` `,` `<->` 를 단어 경계로 사용
    - `{...}` 클러스터, `@NNN;` 희귀 글리프, `'` 변형 등 보존
    - 빈 토큰 제거
    """
    if not eva:
        return []
    parts = WORD_SEP.split(eva)
    return [p for p in (s.strip() for s in parts) if p]


def expand_tokens(corpus_df: pd.DataFrame) -> pd.DataFrame:
    """라인별 EVA 텍스트를 토큰 단위로 폭발."""
    rows: list[dict] = []
    for _, r in corpus_df.iterrows():
        tokens = tokenize_eva(r["eva_text"])
        for pos, tok in enumerate(tokens):
            rows.append({
                "folio_id": r["folio_id"],
                "line_id": r["line_id"],
                "token_pos": pos,
                "token": tok,
                "section": r["section"],
                "currier_lang": r["currier_lang"],
                "scribe": r["scribe"],
                "locator": r["locator"],
                "is_label": r["locator"].startswith(("@L", "&L")),
                "is_paragraph": r["locator"] in ("@P0", "+P0", "*P0"),
            })
    return pd.DataFrame(rows)


def main() -> int:
    text = DATA.read_text(encoding="utf-8", errors="replace")
    corpus, folio_meta = parse_ivtff(text)
    tokens = expand_tokens(corpus)

    corpus.to_parquet(OUT / "corpus.parquet", index=False)
    folio_meta.to_parquet(OUT / "folio_meta.parquet", index=False)
    tokens.to_parquet(OUT / "tokens.parquet", index=False)

    # Currier 분리
    for lang in ["A", "B"]:
        sub_corpus = corpus[corpus["currier_lang"] == lang]
        sub_tokens = tokens[tokens["currier_lang"] == lang]
        sub_corpus.to_parquet(OUT / f"corpus_{lang}.parquet", index=False)
        sub_tokens.to_parquet(OUT / f"tokens_{lang}.parquet", index=False)

    # 게이트 검증 출력
    print("=== Phase 1 Gate Verification ===")
    print(f"Folios: {len(folio_meta)}")
    print(f"Lines: {len(corpus)}")
    print(f"Tokens (total): {len(tokens)}")
    print(f"Unique token types: {tokens['token'].nunique()}")
    print()
    print("Currier A/B distribution (folios):")
    print(folio_meta["currier_lang"].value_counts())
    print()
    print("Section distribution (folios):")
    print(folio_meta["section"].value_counts())
    print()
    print("Scribe distribution:")
    print(folio_meta["scribe"].value_counts())
    print()
    print("Tokens by Currier:")
    print(tokens["currier_lang"].value_counts())

    # 게이트 통과 조건 체크
    n_tokens = len(tokens)
    n_folios = len(folio_meta)
    cur_a = (folio_meta["currier_lang"] == "A").sum()
    cur_b = (folio_meta["currier_lang"] == "B").sum()

    gate_pass = True
    if not (35000 <= n_tokens <= 45000):
        print(f"⚠️  Token count {n_tokens} outside expected ~37k range")
        gate_pass = False
    if cur_a < 90 or cur_b < 60:
        print(f"⚠️  Currier A/B = {cur_a}/{cur_b} below expected 100/70")
        gate_pass = False

    if gate_pass:
        print("\n✅ Phase 1 gate PASSED")
    else:
        print("\n❌ Phase 1 gate FAILED — see warnings")
    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())

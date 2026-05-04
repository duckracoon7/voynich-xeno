"""
Phase 8 — 폴리오별 interlinear gloss

각 폴리오의 EVA 라인 위에 카테고리/후보 의미를 병기한 *불완전 번역*.

전략:
  - 토큰을 카테고리로 치환 (Phase 7의 cluster category)
  - 빈도/서포트가 충분한 토큰만 후보 의미 표기
  - 모르는 토큰은 "?"로 표기
  - 명시적 신뢰도 표기 (token freq, in-folio context)

산출:
  artifacts/translation/<folio_id>.gloss.md  — 폴리오별 gloss
  artifacts/translation/index.md             — gloss 폴리오 목록
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
DIC = ROOT / "artifacts" / "dictionary"
OUT = ROOT / "artifacts" / "translation"
OUT.mkdir(parents=True, exist_ok=True)

# 우선 gloss를 만들 폴리오 (label-rich + 다양한 섹션)
GLOSS_FOLIOS = [
    # pharmaceutical (label-anchor 가장 강함)
    "f88r", "f99r",
    # zodiac (인물별 라벨)
    "f70v1", "f71r",
    # astronomical (별-라벨)
    "f68r1",
    # biological (qokain anchor 검증용)
    "f78r", "f79v",
    # herbal sample
    "f1v", "f3r",
    # recipes (별 카운트)
    "f107r", "f113r",
]


def gloss_token(tok: str, dictdf: pd.DataFrame) -> str:
    """단일 토큰을 카테고리/anchor 정보로 변환."""
    rows = dictdf[dictdf["token"] == tok]
    if rows.empty:
        return f"{tok} [UNK]"
    r = rows.iloc[0]
    freq = int(r["freq"])
    cat = r.get("category", "?")
    anchors = r.get("top_anchors", "")
    # confidence ≈ freq → tier 분류
    if freq >= 100:
        conf = "very_common"
    elif freq >= 30:
        conf = "common"
    elif freq >= 10:
        conf = "moderate"
    else:
        conf = "rare"
    # 가장 강한 anchor 1개만 추출 (top_anchors는 PMI 정렬됨)
    if anchors and "no positive" not in anchors:
        first = anchors.split(" | ")[0]
        m = re.match(r"(\w+)\(npmi=([+\-\d.]+),", first)
        if m and float(m.group(2)) > 0.2:
            return f"{tok}[{m.group(1)}|{conf}]"
    return f"{tok}[{conf}]"


def write_folio_gloss(folio_id: str, corpus: pd.DataFrame, dictdf: pd.DataFrame) -> None:
    folio = corpus[corpus["folio_id"] == folio_id].sort_values("line_id")
    if folio.empty:
        return
    section = folio["section"].iloc[0]
    out_path = OUT / f"{folio_id}.gloss.md"

    lines: list[str] = []
    lines.append(f"# {folio_id} — interlinear gloss ({section})")
    lines.append("")
    lines.append("> EVA 토큰 위에 카테고리·신뢰도 라벨 병기.")
    lines.append("> 형식: `token[anchor_feature|confidence_tier]`")
    lines.append("> confidence_tier: very_common (≥100) / common (≥30) / moderate (≥10) / rare (<10)")
    lines.append("> anchor_feature: PMI > 0.2 인 가장 강한 시각적 특성 1개")
    lines.append("> [UNK] = 사전에 등재되지 않음 (대개 hapax)")
    lines.append("")
    lines.append(f"| line | locator | EVA | gloss |")
    lines.append(f"|---|---|---|---|")

    for _, row in folio.iterrows():
        eva = row["eva_text"]
        if not eva:
            continue
        # 토큰화
        tokens = [
            t for t in eva.replace("<->", ".").replace(",", ".").split(".") if t
        ]
        gl = " ".join(gloss_token(t, dictdf) for t in tokens)
        lines.append(f"| {row['line_id']} | `{row['locator']}` | `{eva}` | {gl} |")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_index(folio_ids: list[str]) -> None:
    lines = ["# Voynich interlinear gloss — 인덱스", ""]
    lines.append("**Note**: 이 gloss는 *결정론적 번역*이 아니라 *카테고리 + 신뢰도*만 보여주는")
    lines.append("불완전 번역. anchor_feature는 PMI > 0.2 인 시각적 특성 — 의미 후보지 확정 의미가 아님.")
    lines.append("")
    lines.append("## 처리된 폴리오")
    for fid in folio_ids:
        lines.append(f"- [{fid}]({fid}.gloss.md)")
    (OUT / "index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    corpus = pd.read_parquet(COR / "corpus.parquet")
    dictdf = pd.read_parquet(DIC / "dictionary.parquet")

    for fid in GLOSS_FOLIOS:
        write_folio_gloss(fid, corpus, dictdf)
        print(f"  wrote {fid}.gloss.md")

    write_index(GLOSS_FOLIOS)
    print(f"\n✅ Phase 8 gloss complete — {len(GLOSS_FOLIOS)} folios in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

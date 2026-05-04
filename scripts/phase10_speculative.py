"""
Phase 10 — 추정 재구성 번역 (Speculative Reconstruction)

⚠️ 이것은 *결정론적 번역*이 아닙니다. 각 토큰의 가장 강한 시각적 anchor를
   자연어 hint로 치환한 *재구성*. 실제 의미와 다를 수 있음.

방법:
  1. 각 토큰의 top-1 anchor (NPMI > 0.2)를 한국어/영어 명사 hint로 매핑
  2. 강한 신호 없는 흔한 토큰 → 기능어 후보 ("the", "of", "a")
  3. UNK 토큰 → "?" 또는 EVA 원형 유지
  4. label / paragraph 위치에 따라 표시 방식 차별

산출:
  artifacts/translation/<folio>.translation.md
    - EVA 원문
    - 토큰별 추정 gloss
    - 한국어 추정 재구성
    - 영어 추정 재구성
    - 신뢰도 표시
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

# Anchor feature → 자연어 hint
FEATURE_GLOSS_KO = {
    "n_nymphs": "사람", "n_human_figures": "사람들", "has_human_figure": "사람",
    "has_water": "물", "n_pools": "풀", "n_pipes": "관",
    "n_containers": "용기", "has_container": "용기",
    "n_plant_fragments": "식물조각", "fragments_are_whole_plants": "식물",
    "n_leaves_visible": "잎", "n_flowers_visible": "꽃",
    "branching_depth": "가지", "n_petals": "꽃잎",
    "n_stars": "별", "n_red_stars": "붉은별", "n_tailed_stars": "꼬리별",
    "has_star_motif": "별표", "has_central_star": "중심별",
    "has_circular_structure": "원반", "has_radial_symmetry": "방사",
    "n_concentric_rings": "동심원", "n_rays": "광선", "n_rays_or_petals": "광선",
    "has_sun_face": "해", "has_moon_face": "달",
    "has_T_O_diagram": "TO도해", "has_spiral": "나선", "spiral_turns": "나선",
    "n_beads": "구슬", "has_central_object": "중심물체",
    "n_text_blocks": "글덩이", "n_visual_text_columns": "글단",
    "n_distinct_objects": "객체", "n_labels": "라벨",
    "n_colors_used": "색", "n_decorative_motifs": "장식",
    "n_paragraphs": "단락", "n_rows": "행",
    "has_marginal_annotation": "마진주석",
}
FEATURE_GLOSS_EN = {
    "n_nymphs": "person", "n_human_figures": "people", "has_human_figure": "person",
    "has_water": "water", "n_pools": "pool", "n_pipes": "pipe",
    "n_containers": "vessel", "has_container": "vessel",
    "n_plant_fragments": "plant-part", "fragments_are_whole_plants": "plant",
    "n_leaves_visible": "leaf", "n_flowers_visible": "flower",
    "branching_depth": "branch", "n_petals": "petal",
    "n_stars": "star", "n_red_stars": "red-star", "n_tailed_stars": "comet",
    "has_star_motif": "star", "has_central_star": "center-star",
    "has_circular_structure": "circle", "has_radial_symmetry": "radial",
    "n_concentric_rings": "ring", "n_rays": "ray", "n_rays_or_petals": "ray",
    "has_sun_face": "sun", "has_moon_face": "moon",
    "has_T_O_diagram": "T-O", "has_spiral": "spiral", "spiral_turns": "spiral",
    "n_beads": "bead", "has_central_object": "center-thing",
    "n_text_blocks": "block", "n_visual_text_columns": "column",
    "n_distinct_objects": "object", "n_labels": "label",
    "n_colors_used": "color", "n_decorative_motifs": "ornament",
    "n_paragraphs": "para", "n_rows": "row",
    "has_marginal_annotation": "margin-note",
}

# 추정 기능어 후보 (very_common + label_pct < 0.05 + no strong anchor)
FUNCTION_KO = {"daiin": "그것", "ol": "의", "aiin": "그", "ar": "을", "or": "은",
               "chol": "있다", "chor": "이다", "dy": "는", "s": "도",
               "chey": "또", "cheey": "그리고", "shey": "있고", "okeey": "한",
               "okeedy": "있는"}
FUNCTION_EN = {"daiin": "(it)", "ol": "(of)", "aiin": "(the)", "ar": "(at)", "or": "(is)",
               "chol": "(has)", "chor": "(of-A)", "dy": "(s)", "s": "(also)",
               "chey": "(and)", "cheey": "(also)", "shey": "(then)", "okeey": "(one)",
               "okeedy": "(those)"}


def load_dict() -> dict[str, dict]:
    """token → { freq, top_anchor_feature, top_anchor_npmi, in_label_pct, ... }."""
    df = pd.read_parquet(DIC / "dictionary.parquet")
    pmi = pd.read_parquet(DIC / "token_feature_pmi.parquet")
    pmi["score"] = pmi["npmi"] * pmi["support"].pow(0.5)
    top = (
        pmi[pmi["npmi"] > 0]
        .sort_values(["token", "score"], ascending=[True, False])
        .groupby("token")
        .head(1)
        .set_index("token")
    )
    out = {}
    for _, r in df.iterrows():
        tok = r["token"]
        info = {"freq": int(r["freq"]),
                "in_label_pct": float(r["in_label_pct"]),
                "in_paragraph_pct": float(r["in_paragraph_pct"])}
        if tok in top.index:
            tt = top.loc[tok]
            info["top_feature"] = tt["feature"]
            info["top_npmi"] = float(tt["npmi"])
        else:
            info["top_feature"] = None
            info["top_npmi"] = 0.0
        out[tok] = info
    return out


def gloss_token(tok: str, info: dict | None, lang: str) -> tuple[str, str]:
    """반환: (text, marker). marker는 신뢰도 표시 (★ ✦ ☆ ?)."""
    if info is None:
        # UNK
        return f"⟨{tok}⟩", "?"

    npmi = info.get("top_npmi", 0.0)
    feat = info.get("top_feature")
    freq = info["freq"]
    label_pct = info["in_label_pct"]

    # 기능어 후보: 빈도 매우 높고 anchor 약함
    if freq >= 100 and (feat is None or npmi < 0.15) and label_pct < 0.05:
        d = FUNCTION_KO if lang == "ko" else FUNCTION_EN
        return d.get(tok, f"⟨{tok}⟩"), "☆"

    if feat is None or npmi <= 0:
        return f"⟨{tok}⟩", "?"

    # anchor 강도에 따른 마커
    if npmi >= 0.4:
        marker = "★"
    elif npmi >= 0.25:
        marker = "✦"
    else:
        marker = "☆"

    table = FEATURE_GLOSS_KO if lang == "ko" else FEATURE_GLOSS_EN
    word = table.get(feat, feat)
    # 라벨 위치는 명사형으로 강조, 본문은 동사/형용사 가능성
    if label_pct >= 0.5:
        return f"⟪{word}⟫", marker  # 라벨
    else:
        return word, marker


def translate_folio(
    folio_id: str, corpus: pd.DataFrame, dictinfo: dict
) -> tuple[str, str, str]:
    """폴리오 → (eva_lines, ko_translation, en_translation)"""
    folio = corpus[corpus["folio_id"] == folio_id].sort_values("line_id")
    eva_lines, ko_lines, en_lines = [], [], []
    for _, row in folio.iterrows():
        eva = row["eva_text"]
        if not eva:
            continue
        toks = [t for t in eva.replace("<->", ".").replace(",", ".").split(".") if t]
        ko_glosses = [gloss_token(t, dictinfo.get(t), "ko") for t in toks]
        en_glosses = [gloss_token(t, dictinfo.get(t), "en") for t in toks]
        ko = " ".join(f"{w}{m}" if m != "?" else w for w, m in ko_glosses)
        en = " ".join(f"{w}{m}" if m != "?" else w for w, m in en_glosses)
        eva_lines.append(f"  L{row['line_id']:>3} [{row['locator']}]: {eva}")
        ko_lines.append(f"  L{row['line_id']:>3}: {ko}")
        en_lines.append(f"  L{row['line_id']:>3}: {en}")
    return "\n".join(eva_lines), "\n".join(ko_lines), "\n".join(en_lines)


HEADER_TMPL = """# {fid} — 추정 재구성 번역 (Speculative Reconstruction)

> ⚠️ **이것은 결정론적 번역이 아니다.**
>
> 각 토큰을 그 *시각적 anchor*로 치환한 재구성. 의미는 영영 모를 수 있음.
> 신뢰도 표지: ★ NPMI≥0.4, ✦ NPMI≥0.25, ☆ 약함, ? 미상
>
> ⟪이중꺾쇠⟫ = 라벨 위치 (명사 가능성 높음)
> ⟨꺾쇠⟩ = UNK 또는 anchor 없음

## EVA 원문

```
{eva}
```

## 한국어 추정 재구성

```
{ko}
```

## English speculative reconstruction

```
{en}
```

## 면책

- 이 번역은 *외부 ground truth* 없이 *우리 자신의 이미지 노트*에서 도출됨 (자기 입력 의존).
- 토큰 → anchor → 의미 후보의 매핑은 통계적으로 유의 (Phase 9 순열검정 50/50 p<0.01)이지만,
  *anchor 자체의 의미는 추측*임. "사람"이 정말 "사람"을 가리킨다는 보장 없음.
- hapax 6,760개는 무시됨 (사전에 없음).
"""


def main() -> int:
    corpus = pd.read_parquet(COR / "corpus.parquet")
    dictinfo = load_dict()

    # 처리 대상: Phase 8과 같은 폴리오 + 추가 sample
    targets = [
        "f88r", "f99r",          # pharmaceutical
        "f70v1", "f71r",         # zodiac
        "f68r1",                 # astronomical
        "f78r", "f79v",          # biological
        "f1v", "f3r", "f25r",    # herbal
        "f107r", "f113r",        # recipes
        "f69r",                  # cosmological
    ]
    for fid in targets:
        eva, ko, en = translate_folio(fid, corpus, dictinfo)
        if not eva:
            continue
        path = OUT / f"{fid}.translation.md"
        path.write_text(HEADER_TMPL.format(fid=fid, eva=eva, ko=ko, en=en))
        print(f"  wrote {path.name}")

    # 인덱스 업데이트
    idx_lines = ["# 보이니치 추정 재구성 번역 — 인덱스", ""]
    idx_lines.append("## ⚠️ 면책")
    idx_lines.append("")
    idx_lines.append("이 번역은 **결정론적 의미**가 아닌 **시각적 anchor 기반 추정**.")
    idx_lines.append("")
    idx_lines.append(f"- 사전 커버리지: 71.1% (instance), 10.8% (unique types)")
    idx_lines.append(f"- 통계적 유의성: 상위 50 anchor 페어 모두 p<0.01")
    idx_lines.append(f"- Bootstrap Procrustes Recall@5: 0.668 [0.499, 0.810]")
    idx_lines.append("")
    idx_lines.append("## 폴리오별 번역 (안전 우선순위 — label-rich 순)")
    idx_lines.append("")
    for fid in targets:
        idx_lines.append(f"- [{fid}]({fid}.translation.md)")
    idx_lines.append("")
    idx_lines.append("## 같이 보는 자료")
    idx_lines.append("- [신뢰도 보고서](../dictionary/reliability_report.md)")
    idx_lines.append("- [사전 (CSV)](../dictionary/dictionary.csv)")
    idx_lines.append("- [순열 검정 결과](../dictionary/permutation_test.json)")
    idx_lines.append("- [Bootstrap CI](../dictionary/bootstrap_recall.json)")
    (OUT / "translation_index.md").write_text("\n".join(idx_lines))

    print(f"\n✅ Phase 10 speculative translation complete — {len(targets)} folios")
    print(f"   See {OUT / 'translation_index.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

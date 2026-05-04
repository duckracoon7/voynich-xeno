"""
Phase 13 — 226 폴리오 전부에 xeno-reading 자동 생성

f78r/f1v/f70v1의 손으로 다듬은 산문은 *고품질 표본*. 본 스크립트는 그 형식을
모방한 자동 생성으로 226 폴리오 모두를 채운다.

품질 정직 기준:
  - 신호 강한 페이지 = 풍부한 산문
  - placeholder 페이지 (herbal 124) = 짧은 stub
  - 모든 페이지에 동일한 *데이터 검증 표* 첨부
  - 모든 페이지에 동일한 면책 명시

산출:
  artifacts/xeno_reading/auto/<folio_id>.xeno.md  (총 226개)
  artifacts/xeno_reading/auto/index.md
"""
from __future__ import annotations
import json
import re
import sys
import random
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
DIC = ROOT / "artifacts" / "dictionary"
IMG = ROOT / "image_descriptions"
OUT = ROOT / "artifacts" / "xeno_reading" / "auto"
OUT.mkdir(parents=True, exist_ok=True)

VISION_FIELDS = [
    "n_text_blocks", "n_visual_text_columns", "n_distinct_objects", "n_labels",
    "n_colors_used", "n_decorative_motifs", "has_circular_structure",
    "has_radial_symmetry", "has_human_figure", "has_container", "has_water",
    "has_sun_face", "has_moon_face", "has_marginal_annotation", "has_spiral",
    "has_T_O_diagram", "has_central_star", "has_central_object", "has_star_motif",
    "fragments_are_whole_plants", "n_stars", "n_concentric_rings",
    "n_human_figures", "n_containers", "n_plant_fragments", "n_rows",
    "n_paragraphs", "n_petals", "n_rays", "n_leaves_visible", "n_flowers_visible",
    "branching_depth", "n_red_stars", "n_tailed_stars", "n_nymphs", "n_pools",
    "n_pipes", "spiral_turns", "n_beads", "n_rays_or_petals",
]


def parse_yaml(text: str) -> dict:
    blocks = re.findall(r"```yaml\s*\n(.*?)\n```", text, re.DOTALL)
    flat: dict = {}
    for block in blocks:
        for line in block.splitlines():
            m = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if not m:
                continue
            key, val = m.group(1), m.group(2).split("#")[0].strip()
            if not val or val.startswith(("[", "{")):
                continue
            if val.lower() in ("true", "false"):
                flat[key] = 1.0 if val.lower() == "true" else 0.0
            elif val.lower() in ("null", "none", "___"):
                continue
            elif val.startswith('"') and val.endswith('"'):
                flat[key] = val.strip('"')
            else:
                try:
                    flat[key] = float(val)
                except ValueError:
                    flat[key] = val
    return flat


# =============================================================
# 페이지별 prose generator — 섹션별 전략
# =============================================================

# Hand-crafted 페이지는 generator를 우회 (이미 정성껏 작성됨)
SKIP_FOLIOS = {"f1v", "f78r", "f70v1"}  # already in xeno_reading/


def is_placeholder(folio_id: str, section: str) -> bool:
    md = IMG / section / f"{folio_id}.md"
    if not md.exists():
        return False
    return 'detail_status: "generic_placeholder"' in md.read_text(encoding="utf-8")


def page_anchors(folio_id: str, corpus: pd.DataFrame, pmi_df: pd.DataFrame,
                 dictdf: pd.DataFrame, k: int = 6) -> list[dict]:
    """폴리오에 등장하는 토큰들의 top anchor 집계."""
    folio_tokens = corpus[corpus["folio_id"] == folio_id]
    tokens_set = set()
    for _, row in folio_tokens.iterrows():
        eva = row["eva_text"]
        if not eva:
            continue
        tokens_set.update(
            t for t in eva.replace("<->", ".").replace(",", ".").split(".") if t
        )

    relevant = pmi_df[pmi_df["token"].isin(tokens_set) & (pmi_df["npmi"] > 0.15)]
    if relevant.empty:
        return []
    # 페이지 신호 = 토큰별 top anchor의 점수 합
    relevant = relevant.assign(score=relevant["npmi"] * np.sqrt(relevant["support"]))
    by_feat = relevant.groupby("feature").agg(
        max_npmi=("npmi", "max"),
        sum_score=("score", "sum"),
        n_tokens=("token", "nunique"),
    ).sort_values("sum_score", ascending=False).reset_index()
    return by_feat.head(k).to_dict("records")


# 섹션별 도입부 prose 변형 (랜덤 선택)
HERBAL_OPENINGS = [
    "이 페이지에는 한 형상이 한 그루로 서 있다.",
    "한 형상이 페이지의 한 자리를 차지한다.",
    "줄기와 잎과 뿌리로 이루어진 한 단위가 여기에 있다.",
    "한 형상이 곧게 또는 비스듬히 그려져 있다.",
]
ASTRONOMICAL_OPENINGS = [
    "별이 페이지에 흩어진다.",
    "이 페이지는 별의 자리를 적은 도해다 — 또는 그렇게 보인다.",
    "여러 점이 한 자리를 둘러싼다.",
]
ZODIAC_OPENINGS = [
    "원형 도해가 페이지를 채운다. 가운데에 한 형상이 있다.",
    "동심의 원과 그 안에 늘어선 사람과 별이 짝을 이룬다.",
    "원이 동심으로 그려지고, 그 둘레마다 형상들이 늘어선다.",
]
BIOLOGICAL_OPENINGS = [
    "사람의 형상이 풀과 관 사이에 놓여 있다.",
    "물과 사람과 관이 페이지에 함께 있다.",
    "형상들이 물의 자리에 들어가거나 그 가장자리에 선다.",
]
PHARMACEUTICAL_OPENINGS = [
    "용기와 식물조각이 행을 이루어 늘어선다.",
    "단지가 한 쪽에 있고 그 옆으로 부분들이 흩어져 있다.",
    "용기와 부분과 본문이 같은 행에 묶여 반복된다.",
]
COSMOLOGICAL_OPENINGS = [
    "원형의 큰 도해가 페이지를 차지한다.",
    "동심·방사·중심을 가진 도해가 한 자리에 있다.",
    "가운데에서 바깥으로 무엇인가 펼쳐진다.",
]
RECIPES_OPENINGS = [
    "그림 없이 본문이 흐르고, 단락마다 별 하나가 마진에 붙는다.",
    "이 페이지에는 도해가 없다. 단락과 별이 짝을 이룬다.",
    "본문만이 페이지를 채우고, 마진의 별이 단락의 시작을 표시한다.",
]
TEXT_OPENINGS = [
    "이 페이지는 본문 위주다. 도해는 거의 없거나 전혀 없다.",
    "글이 페이지를 채운다. 그림 자리는 좁거나 비어 있다.",
]
SECTION_OPENINGS = {
    "herbal": HERBAL_OPENINGS,
    "astronomical": ASTRONOMICAL_OPENINGS,
    "zodiac": ZODIAC_OPENINGS,
    "biological": BIOLOGICAL_OPENINGS,
    "pharmaceutical": PHARMACEUTICAL_OPENINGS,
    "cosmological": COSMOLOGICAL_OPENINGS,
    "recipes": RECIPES_OPENINGS,
    "text": TEXT_OPENINGS,
}


# Anchor feature → xeno-style 한국어 명사
ANCHOR_NOUN = {
    "n_nymphs": "사람", "n_human_figures": "사람", "has_human_figure": "사람",
    "has_water": "물", "n_pools": "풀", "n_pipes": "관",
    "n_containers": "용기", "has_container": "용기",
    "n_plant_fragments": "부분", "fragments_are_whole_plants": "단위",
    "n_leaves_visible": "면", "n_flowers_visible": "갓", "branching_depth": "가지",
    "n_petals": "잎",
    "n_stars": "빛점", "n_red_stars": "붉은 점", "n_tailed_stars": "꼬리진 점",
    "has_star_motif": "별표", "has_central_star": "중심점",
    "has_circular_structure": "원", "has_radial_symmetry": "방사",
    "n_concentric_rings": "동심", "n_rays": "광선", "n_rays_or_petals": "광선",
    "has_sun_face": "해", "has_moon_face": "달",
    "has_T_O_diagram": "T-O 도해", "has_spiral": "나선", "spiral_turns": "회전",
    "n_beads": "구슬", "has_central_object": "중심 단위",
    "n_text_blocks": "글덩이", "n_visual_text_columns": "글의 단",
    "n_distinct_objects": "객체", "n_labels": "라벨", "n_colors_used": "색",
    "n_decorative_motifs": "장식", "n_paragraphs": "단락", "n_rows": "행",
    "has_marginal_annotation": "마진의 주석",
}


def visual_summary(meta: dict, section: str) -> str:
    """이미지 YAML에서 시각 사실 추출하여 한 문장."""
    parts: list[str] = []

    if section == "herbal":
        n_l = int(meta.get("n_leaves_visible", 0) or 0)
        n_f = int(meta.get("n_flowers_visible", 0) or 0)
        if n_l:
            parts.append(f"잎 약 {n_l}장")
        if n_f:
            parts.append(f"꽃 {n_f}개")
        if meta.get("has_root", 0):
            parts.append("뿌리")

    elif section == "astronomical":
        n_s = int(meta.get("n_stars", 0) or 0)
        n_r = int(meta.get("n_concentric_rings", 0) or 0)
        if n_s:
            parts.append(f"별 약 {n_s}개")
        if n_r:
            parts.append(f"동심 {n_r}겹")
        if meta.get("has_sun_face", 0):
            parts.append("해 얼굴")
        if meta.get("has_moon_face", 0):
            parts.append("달 얼굴")

    elif section == "zodiac":
        n_h = int(meta.get("n_human_figures", 0) or 0)
        n_r = int(meta.get("n_concentric_rings", 0) or 0)
        if n_h:
            parts.append(f"사람 약 {n_h}명")
        if n_r:
            parts.append(f"동심 {n_r}겹")

    elif section == "biological":
        n_n = int(meta.get("n_nymphs", 0) or 0)
        n_p = int(meta.get("n_pools", 0) or 0)
        n_pi = int(meta.get("n_pipes", 0) or 0)
        if n_n:
            parts.append(f"사람 {n_n}명")
        if n_p:
            parts.append(f"풀 {n_p}개")
        if n_pi:
            parts.append(f"관 {n_pi}개")

    elif section == "pharmaceutical":
        n_c = int(meta.get("n_containers", 0) or 0)
        n_pf = int(meta.get("n_plant_fragments", 0) or 0)
        n_r = int(meta.get("n_rows", 0) or 0)
        if n_c:
            parts.append(f"용기 {n_c}개")
        if n_pf:
            parts.append(f"부분 {n_pf}조각")
        if n_r:
            parts.append(f"{n_r}행 구조")

    elif section == "cosmological":
        n_r = int(meta.get("n_concentric_rings", 0) or 0)
        n_p = int(meta.get("n_rays_or_petals", 0) or 0)
        if n_r:
            parts.append(f"동심 {n_r}겹")
        if n_p:
            parts.append(f"광선/잎 {n_p}개")

    elif section == "recipes":
        n_para = int(meta.get("n_paragraphs", 0) or 0)
        n_st = int(meta.get("n_stars", 0) or 0)
        if n_para:
            parts.append(f"단락 {n_para}개")
        if n_st:
            parts.append(f"마진 별 {n_st}개")

    if not parts:
        n_t = int(meta.get("n_text_blocks", 0) or 0)
        if n_t:
            parts.append(f"글덩이 {n_t}개")

    return " · ".join(parts) if parts else "구체적 시각 신호 빈약"


def speculation_paragraph(anchors: list[dict], section: str, rng: random.Random) -> str:
    """anchor 신호들을 한 문단으로 엮음."""
    if not anchors:
        return "이 페이지에서 우리 사전이 잡아낸 신호는 매우 약하다. " \
               "anchor가 거의 비어 있으므로, 본문이 무엇을 말하는지에 대해 " \
               "데이터 기반의 추측은 거의 불가능하다."

    nouns = []
    for a in anchors[:5]:
        feat = a["feature"]
        if feat in ANCHOR_NOUN:
            nouns.append((ANCHOR_NOUN[feat], float(a["max_npmi"]), int(a["n_tokens"])))
    if not nouns:
        return "anchor가 모두 추상 통계 신호여서 한국어 명사로 옮기지 못했다."

    # 강도 정렬
    nouns.sort(key=lambda x: -x[1])
    primary = nouns[0]
    secondary = nouns[1:3]

    sentences = []

    sentences.append(
        f"이 페이지에 등장하는 단어들 가운데 *{primary[0]}*과 가장 강하게 짝지어지는 "
        f"것이 있다. 그 짝의 강도(NPMI={primary[1]:+.2f})는 우연으로 보기 어렵다."
    )

    if secondary:
        co = "·".join(f"*{n[0]}*" for n in secondary)
        sentences.append(
            f"같은 페이지의 다른 단어들은 {co}와 함께 자주 등장한다. "
            f"이 짝짓기가 *의미*인지 *우연한 공기성*인지를 데이터만으로는 가를 수 없다."
        )

    sentences.append(
        f"우리는 이 짝들이 *{primary[0]}*에 관한 무엇인가를 적은 글로 읽고 싶어진다 — "
        f"그러나 그 욕구는 우리 쪽의 것이지 페이지의 것은 아닐 수 있다."
    )

    return " ".join(sentences)


HEADER_TMPL = """# {fid} — xeno-reading (auto)

> ⚠️ **자동 생성 산문**. 손으로 다듬은 표본(f1v/f78r/f70v1)을 모방한 generator 출력.
> 이는 *번역*이 아니다. 데이터 신호 + 시각 사실의 *constrained imagination* 한 가닥.

## 페이지가 보여주는 것

- **섹션**: {section}  |  **Currier**: {lang}  |  **필경사**: {scribe}{placeholder_note}
- **시각 요약**: {visual}
- **본문 라인**: {n_lines}  |  **단락 시작**: {n_para}  |  **라벨**: {n_labels}

## 한 가지 읽기

{opening}

{spec}

## 페이지에 등장한 단어와 그 anchor

상위 {n_anchors}개 시각 특성 (NPMI ≥ 0.15, 페이지 토큰 기여 합산):

| anchor | max NPMI | 기여 토큰 수 |
|--------|----------|--------------|
{anchor_table}

## 면책

- 이 산문은 *우리가 만든 사전*에서 *우리가 만든 이미지 노트*로 매핑된 결과를 한국어로 옮긴 것.
- *외부 ground truth* 없음.
- 같은 데이터가 다른 산문으로도 읽힐 수 있다 (*literary_reconstruction/* 참조).
"""


def render_page(folio_id: str, frow, corpus: pd.DataFrame, pmi_df: pd.DataFrame,
                dictdf: pd.DataFrame, rng: random.Random) -> str:
    section = frow["section"]
    md_path = IMG / section / f"{folio_id}.md"
    meta = parse_yaml(md_path.read_text(encoding="utf-8")) if md_path.exists() else {}

    anchors = page_anchors(folio_id, corpus, pmi_df, dictdf)
    visual = visual_summary(meta, section)
    opening = rng.choice(SECTION_OPENINGS.get(section, ["페이지가 펼쳐진다."]))
    spec = speculation_paragraph(anchors, section, rng)

    folio_lines = corpus[corpus["folio_id"] == folio_id]
    n_lines = len(folio_lines)
    n_para = int((folio_lines["locator"].isin(["@P0", "*P0"])).sum())
    n_labels = int(folio_lines["locator"].str.startswith(("@L", "&L")).sum())

    placeholder_note = " ⓟ" if is_placeholder(folio_id, section) else ""

    if anchors:
        rows = []
        for a in anchors:
            rows.append(
                f"| {a['feature']} | {a['max_npmi']:+.3f} | {int(a['n_tokens'])} |"
            )
        anchor_table = "\n".join(rows)
    else:
        anchor_table = "| (no positive-PMI anchor) | — | — |"

    return HEADER_TMPL.format(
        fid=folio_id,
        section=section,
        lang=frow.get("currier_lang", "?") or "?",
        scribe=frow.get("scribe", "?") or "?",
        placeholder_note=placeholder_note,
        visual=visual,
        n_lines=n_lines,
        n_para=n_para,
        n_labels=n_labels,
        opening=opening,
        spec=spec,
        n_anchors=len(anchors),
        anchor_table=anchor_table,
    )


def main() -> int:
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")
    corpus = pd.read_parquet(COR / "corpus.parquet")
    pmi_df = pd.read_parquet(DIC / "token_feature_pmi.parquet")
    dictdf = pd.read_parquet(DIC / "dictionary.parquet")

    rng = random.Random(42)

    rendered = 0
    skipped = []
    placeholder_count = 0
    for _, frow in folio_meta.iterrows():
        fid = frow["folio_id"]
        if fid in SKIP_FOLIOS:
            skipped.append(fid)
            continue
        try:
            md = render_page(fid, frow, corpus, pmi_df, dictdf, rng)
            (OUT / f"{fid}.xeno.md").write_text(md, encoding="utf-8")
            if is_placeholder(fid, frow["section"]):
                placeholder_count += 1
            rendered += 1
        except Exception as e:
            print(f"  FAIL {fid}: {e}")

    # 인덱스 작성
    idx = ["# xeno-reading (auto) — 인덱스", "",
           "> ⚠️ **자동 생성**. 손으로 다듬은 표본(`../f1v.xeno.md`, `../f78r.xeno.md`, "
           "`../f70v1.xeno.md`)은 별도 폴더에 위치.",
           "",
           f"- 자동 생성 페이지: **{rendered}**",
           f"- 그중 placeholder ⓟ (herbal 정밀화 미완): **{placeholder_count}**",
           f"- 손으로 다듬은 표본 (제외): {', '.join(skipped)}", "",
           "## 페이지 목록 (섹션별)", ""]

    section_groups: dict[str, list[str]] = {}
    for _, frow in folio_meta.iterrows():
        fid = frow["folio_id"]
        if fid in SKIP_FOLIOS:
            continue
        section_groups.setdefault(frow["section"], []).append(fid)

    for section in ["text", "herbal", "astronomical", "cosmological", "zodiac",
                    "biological", "pharmaceutical", "recipes"]:
        if section not in section_groups:
            continue
        idx.append(f"### {section} ({len(section_groups[section])})")
        idx.append("")
        for fid in sorted(section_groups[section]):
            ph = " ⓟ" if is_placeholder(fid, section) else ""
            idx.append(f"- [{fid}]({fid}.xeno.md){ph}")
        idx.append("")

    (OUT / "index.md").write_text("\n".join(idx), encoding="utf-8")

    print(f"✅ Rendered: {rendered}/{len(folio_meta)}  "
          f"(placeholder: {placeholder_count}, skipped: {len(skipped)})")
    print(f"   Output: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

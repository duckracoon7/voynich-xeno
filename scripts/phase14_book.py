"""
Phase 14 — 단일 번역본 (voynich_book.md)

226 폴리오를 매뉴스크립트 순서로 *한 권의 책처럼* 흐르는 한국어 산문.
데이터 검증 표·매 페이지 면책 제거. 표지에 한 번만 면책.

산출:
  artifacts/voynich_book.md   (전체 책)
  artifacts/voynich_book_en.md (영어 동시 — optional)
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


# 섹션 → 한국어 표제
SECTION_TITLE = {
    "text": "글의 자리",
    "herbal": "형상의 책",
    "astronomical": "별의 자리",
    "cosmological": "큰 도해",
    "zodiac": "원의 책",
    "biological": "흐름의 책",
    "pharmaceutical": "단지의 책",
    "recipes": "별과 단락",
}


# Anchor → 한국어 명사 (xeno-style, 절제됨)
ANCHOR_NOUN = {
    "n_nymphs": "사람", "n_human_figures": "사람", "has_human_figure": "사람",
    "has_water": "물", "n_pools": "풀", "n_pipes": "관",
    "n_containers": "단지", "has_container": "단지",
    "n_plant_fragments": "부분", "fragments_are_whole_plants": "단위",
    "n_leaves_visible": "면", "n_flowers_visible": "갓", "branching_depth": "가지",
    "n_petals": "잎",
    "n_stars": "빛점", "n_red_stars": "붉은 점", "n_tailed_stars": "꼬리진 점",
    "has_star_motif": "별표", "has_central_star": "중심점",
    "has_circular_structure": "원", "has_radial_symmetry": "방사",
    "n_concentric_rings": "동심", "n_rays": "광선", "n_rays_or_petals": "광선",
    "has_sun_face": "해", "has_moon_face": "달",
    "has_T_O_diagram": "T-O 도해", "has_spiral": "나선", "spiral_turns": "회전",
    "n_beads": "구슬", "has_central_object": "중심",
    "n_paragraphs": "단락",
    "n_rows": "행",
}


# =============================================================
# 섹션별 산문 작성 함수 (book-style: 짧고 단정적)
# =============================================================

def folio_anchors(folio_id: str, corpus, pmi_df, threshold=0.15):
    folio_tokens = corpus[corpus["folio_id"] == folio_id]
    tokens_set = set()
    for _, row in folio_tokens.iterrows():
        eva = row["eva_text"]
        if not eva:
            continue
        tokens_set.update(
            t for t in eva.replace("<->", ".").replace(",", ".").split(".") if t
        )
    relevant = pmi_df[pmi_df["token"].isin(tokens_set) & (pmi_df["npmi"] > threshold)]
    if relevant.empty:
        return []
    relevant = relevant.assign(score=relevant["npmi"] * np.sqrt(relevant["support"]))
    by_feat = (relevant.groupby("feature")
               .agg(max_npmi=("npmi", "max"), sum_score=("score", "sum"))
               .sort_values("sum_score", ascending=False))
    return [(f, ANCHOR_NOUN.get(f, f), float(by_feat.loc[f, "max_npmi"]))
            for f in by_feat.index if f in ANCHOR_NOUN]


def prose_herbal(meta: dict, anchors, rng) -> str:
    n_l = int(meta.get("n_leaves_visible", 0) or 0)
    n_f = int(meta.get("n_flowers_visible", 0) or 0)
    branch = int(meta.get("branching_depth", 0) or 0)
    leaf_shape = meta.get("leaf_shape", "")
    flower_shape = meta.get("flower_shape", "")
    root_style = meta.get("root_style", "")
    is_placeholder = meta.get("detail_status", "") == "generic_placeholder"

    parts = []
    if not is_placeholder:
        sent = "한 형상이 한 그루로 서 있다."
        if n_l and branch:
            sent = f"한 형상이 곧게 서고, 가지가 {branch}단으로 갈라지며 그 끝마다 면이 달린다. 면은 모두 헤아려 약 {n_l}장이다."
        elif n_l:
            sent = f"한 형상이 곧게 서고, 면이 약 {n_l}장 달려 있다."
        parts.append(sent)
        if n_f:
            f_desc = "꼭대기에 갓이 하나 맺힌다." if n_f == 1 else f"꼭대기 가까이에 갓이 {n_f}개 맺힌다."
            if isinstance(flower_shape, str) and flower_shape:
                if "blue" in flower_shape:
                    f_desc = f_desc[:-1] + ", 그 빛은 푸르다."
                elif "tufted" in flower_shape or "thistle" in flower_shape:
                    f_desc = f_desc[:-1] + ", 술처럼 풀어진 모양이다."
            parts.append(f_desc)
        if isinstance(root_style, str) and root_style:
            if "mound" in root_style:
                parts.append("아래는 두 둔덕으로 펼쳐지고, 그 위에 빗금이 빽빽하다.")
            elif "fingered" in root_style or "forked" in root_style:
                parts.append("아래는 손가락 모양으로 갈라져 사방으로 뻗는다.")
            elif "chained" in root_style:
                parts.append("아래는 흔히 보는 뿌리가 아니라, 옆으로 누운 막대에 작은 마디가 박혀 있다.")
            else:
                parts.append("아래는 통상의 뿌리와 같지 않다.")
    else:
        # placeholder — 짧고 일반적
        parts.append("한 형상이 페이지의 한 자리를 차지한다. 그 잎과 가지, 뿌리의 꼴은 같은 책의 다른 형상과 비슷하나 같지 않다.")

    # anchor 1개를 본문 내용 hint로
    if anchors:
        primary = anchors[0]
        nouns = [a[1] for a in anchors[:3]]
        if primary[1] == "단락" or primary[1] == "행":
            parts.append("본문은 줄기를 피해 흐르며, 적힌 바를 우리는 읽지 못한다.")
        else:
            seen = " · ".join(set(nouns[:2]))
            parts.append(f"본문에는 *{seen}*에 관한 단어들이 다른 페이지보다 자주 나타난다. 그것이 무엇을 가리키는지는 알지 못한다.")

    return " ".join(parts)


def prose_astronomical(meta: dict, anchors, rng) -> str:
    n_s = int(meta.get("n_stars", 0) or 0)
    n_r = int(meta.get("n_concentric_rings", 0) or 0)
    has_sun = bool(meta.get("has_sun_face", 0))
    has_moon = bool(meta.get("has_moon_face", 0))
    parts = []
    if has_sun and not has_moon:
        parts.append("가운데에 사람의 얼굴을 두른 해가 있다.")
    elif has_moon and not has_sun:
        parts.append("가운데에 사람의 얼굴을 두른 달이 있다.")
    elif has_sun and has_moon:
        parts.append("가운데에 해와 달이 함께 있다.")
    elif n_r >= 2:
        parts.append("가운데에 작은 점이 있고, 그 둘레로 원이 펼쳐진다.")
    else:
        parts.append("가운데에 작은 점이 있다.")
    if n_s:
        parts.append(f"그 둘레로 빛점이 약 {n_s}개 흩어진다.")
    if n_r >= 2:
        parts.append(f"원이 동심으로 {n_r}겹 그려져 있고, 각 둘레에 점이 늘어선다.")
    if anchors:
        nouns = [a[1] for a in anchors[:3] if a[1] not in ("단락", "행")]
        if nouns:
            parts.append(f"각 점 옆에는 짧은 단어가 적혀 있다 — 우리는 그것을 *{nouns[0]}의 이름*이라 짐작하고 싶어진다.")
    return " ".join(parts)


def prose_cosmological(meta: dict, anchors, rng) -> str:
    n_r = int(meta.get("n_concentric_rings", 0) or 0)
    n_p = int(meta.get("n_rays_or_petals", 0) or 0)
    central = meta.get("central_style", "")
    parts = ["페이지를 큰 원이 차지한다."]
    if n_r:
        parts.append(f"원은 {n_r}겹의 동심으로 그려져 있다.")
    if n_p:
        parts.append(f"가운데에서 바깥으로 광선 또는 잎과 같은 줄기 약 {n_p}개가 뻗는다.")
    if isinstance(central, str) and "rosette" in central:
        parts.append("가운데에는 꽃잎과 같은 무리가 모여 있다.")
    elif isinstance(central, str) and "petal" in central:
        parts.append("가운데에서 꽃잎이 펼쳐지는 모양이 보인다.")
    parts.append("이 도해가 *지도*인지 *역법*인지 *상태도*인지 우리는 정할 수 없다.")
    return " ".join(parts)


def prose_zodiac(meta: dict, anchors, rng) -> str:
    n_h = int(meta.get("n_human_figures", 0) or 0)
    n_r = int(meta.get("n_concentric_rings", 0) or 0)
    central = meta.get("central_emblem", "")
    color = meta.get("central_color", "")
    parts = []
    if isinstance(central, str) and central:
        if "fish" in central:
            parts.append("가운데에 두 형상이 머리와 꼬리를 어긋낸 채 마주 있다.")
        elif "horned" in central or "ram" in central or "goat" in central:
            parts.append("가운데에 뿔 달린 네 발 짐승 한 마리가 서 있다.")
        elif "bull" in central or "horse" in central:
            parts.append("가운데에 네 발 짐승이 한 마리 있고, 그 빛은 붉다." if color == "red" else "가운데에 네 발 짐승이 한 마리 있다.")
        elif "human" in central or "figure" in central:
            color_word = "푸른" if color == "blue" else ""
            parts.append(f"가운데에 {color_word} 옷의 사람 한 명이 있다.")
        elif "balance" in central:
            parts.append("가운데에 저울의 모양을 한 것이 있다.")
        elif "creature" in central:
            parts.append("가운데에 작은 짐승이 있다.")
        else:
            parts.append("가운데에 한 형상이 있다.")
    else:
        parts.append("가운데에 한 형상이 있다.")
    if n_r:
        parts.append(f"그 둘레로 동심의 원이 {n_r}겹 펼쳐진다.")
    if n_h:
        parts.append(f"각 원에 사람이 늘어서 있다. 모두 헤아리면 약 {n_h}명이며, 각자 손에 빛점을 하나씩 들고 있다.")
    parts.append("바깥으로는 둥근 글이 흐른다.")
    return " ".join(parts)


def prose_biological(meta: dict, anchors, rng) -> str:
    n_n = int(meta.get("n_nymphs", 0) or 0)
    n_p = int(meta.get("n_pools", 0) or 0)
    n_pi = int(meta.get("n_pipes", 0) or 0)
    parts = []
    if n_n and n_p:
        parts.append(f"사람 {n_n}명이 풀 {n_p}개의 안과 가장자리에 놓여 있다.")
    elif n_n:
        parts.append(f"사람이 {n_n}명 있다.")
    elif n_p:
        parts.append(f"풀이 {n_p}개 있고, 그 둘레에 사람이 있다.")
    if n_pi:
        parts.append(f"사람과 사람을, 풀과 풀을 잇는 관이 {n_pi}개 보인다.")
    parts.append("물은 푸른빛이며, 한 자리에서 다른 자리로 이어진다.")
    if anchors:
        primary = anchors[0]
        if primary[1] == "사람" and primary[2] > 0.5:
            parts.append("이 페이지에 등장하는 단어들 가운데 사람과 가장 강하게 짝지어지는 것이 있다 — 그 짝의 강도는 우연이라 보기 어렵다.")
    return " ".join(parts)


def prose_pharmaceutical(meta: dict, anchors, rng) -> str:
    n_c = int(meta.get("n_containers", 0) or 0)
    n_pf = int(meta.get("n_plant_fragments", 0) or 0)
    n_r = int(meta.get("n_rows", 0) or 0)
    parts = []
    if n_c:
        parts.append(f"단지 {n_c}개가 한 쪽에 늘어선다.")
    if n_pf:
        parts.append(f"부분 {n_pf}조각이 단지 옆에 흩어져 있다.")
    if n_r:
        parts.append(f"전체는 {n_r}개의 행으로 묶이며, 각 행은 단지 하나, 부분 여럿, 본문 단락 하나로 이루어진다.")
    parts.append("어느 부분이 어느 단지로 들어가는지 — 적힌 바를 우리는 읽지 못한다.")
    return " ".join(parts)


def prose_recipes(meta: dict, anchors, rng) -> str:
    n_para = int(meta.get("n_paragraphs", 0) or 0)
    n_st = int(meta.get("n_stars", 0) or 0)
    parts = []
    if n_para:
        parts.append(f"이 페이지에 그림은 없다. 단락이 {n_para}개 흐르고, 각 단락의 시작 옆 마진에 작은 빛점이 하나씩 붙어 있다.")
    else:
        parts.append("이 페이지에 그림은 없다. 본문이 처음부터 끝까지 흐른다.")
    parts.append("어떤 점은 붉고, 어떤 점은 꼬리가 있다.")
    parts.append("점의 모양이 단락의 무게를 매기는 듯 하나, 그 무게가 무엇의 무게인지는 모른다.")
    return " ".join(parts)


def prose_text(meta: dict, anchors, rng) -> str:
    has_marg = bool(meta.get("has_marginal_annotation", 0))
    parts = ["이 페이지에 도해는 없거나 매우 작다. 글이 페이지의 거의 전부를 채운다."]
    if has_marg:
        parts.append("마진에는 후대의 손이 적었을 것으로 보이는 짧은 표시들이 있다.")
    return " ".join(parts)


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


# =============================================================
# 페이지 순서 정렬
# =============================================================

def folio_sort_key(fid: str) -> tuple:
    """f1r → (1, 'r', 0). f67r1 → (67, 'r', 1)."""
    m = re.match(r"f(\d+)([rv])(\d?)", fid)
    if m:
        return (int(m.group(1)), 0 if m.group(2) == "r" else 1,
                int(m.group(3)) if m.group(3) else 0)
    return (999, 0, 0)


PREFACE = """# 보이니치 (Beinecke MS 408) — 추측 재구성 번역

> ⚠️ **이것은 보이니치 문서의 번역이 아닙니다.**
>
> 이 책은 다음을 결합한 *추측 재구성*입니다:
> 1. 페이지가 *시각적으로* 보여주는 사실 (그림에서 직접 관찰)
> 2. 토큰-시각특성 anchor의 통계적 신호 (Phase 7-9에서 입증, p<0.01)
> 3. 데이터에 *없는 부분*을 메우기 위한 우리의 상상
>
> 보이니치는 600년간 해독되지 않았습니다. 이 책은 그 자리에 *읽힐 수 있는 글*을 놓아본 시도이지,
> 어떤 단어가 *무엇을 의미하는지*에 대한 주장이 아닙니다.
>
> 같은 데이터에서 *전혀 다른 책*도 만들 수 있습니다.
> 우리는 그 한 갈래를 골랐습니다.
>
> 데이터 출처와 anchor 검증은 [`xeno_reading/auto/<folio>.xeno.md`](xeno_reading/auto/) 참조.
> 통계적 유의성 보고서는 [`dictionary/reliability_report.md`](dictionary/reliability_report.md).

---

## 책의 구조

원본은 6–8개의 시각적으로 구별되는 부분으로 나뉩니다. 본 번역도 그 부분 구분을 따릅니다.

- **첫 글** — `f1r` (그림 없음, 도입부로 추정)
- **형상의 책** (herbal) — 한 그루씩 그려진 형상들
- **별의 자리** (astronomical) — 별과 해와 달의 도해
- **큰 도해** (cosmological) — 동심의 원과 방사형 무늬
- **원의 책** (zodiac) — 원형 휠과 그 안의 사람·짐승
- **흐름의 책** (biological) — 사람과 풀과 관
- **단지의 책** (pharmaceutical) — 단지와 부분
- **별과 단락** (recipes) — 그림 없는 본문, 마진의 별

각 폴리오 표제 옆의 작은 표지:
- **A/B**: Currier 방언 분류 (두 손이 두 결로 적음)
- **ⓟ**: herbal 페이지 중 정밀 관찰이 미완인 폴리오 (아래 산문은 일반화된 형태)

---

"""


def main() -> int:
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")
    corpus = pd.read_parquet(COR / "corpus.parquet")
    pmi_df = pd.read_parquet(DIC / "token_feature_pmi.parquet")

    # 폴리오를 매뉴스크립트 순서로 정렬
    folio_meta = folio_meta.assign(
        sort_key=folio_meta["folio_id"].apply(folio_sort_key)
    ).sort_values("sort_key").reset_index(drop=True)

    rng = random.Random(42)

    out: list[str] = [PREFACE]

    # 섹션별로 묶어서 흐름. 각 섹션이 처음 나올 때 큰 표제.
    sections_seen: set[str] = set()
    section_order_korean = SECTION_TITLE

    # 첫 글 (f1r) 따로
    f1r = folio_meta[folio_meta["folio_id"] == "f1r"]
    if not f1r.empty:
        frow = f1r.iloc[0]
        section = frow["section"]
        out.append(f"## 첫 글\n")
        md_path = IMG / section / "f1r.md"
        meta = parse_yaml(md_path.read_text(encoding="utf-8")) if md_path.exists() else {}
        anchors = folio_anchors("f1r", corpus, pmi_df)
        prose = SECTION_FN[section](meta, anchors, rng) if section in SECTION_FN else ""
        out.append(f"### f1r\n\n{prose}\n")
        sections_seen.add("text")

    # 나머지 섹션별 그룹핑하여 작성
    for _, frow in folio_meta.iterrows():
        fid = frow["folio_id"]
        if fid == "f1r":
            continue
        section = frow["section"]
        if section not in section_order_korean:
            continue

        # 새 섹션 진입 시 표제
        if section not in sections_seen:
            out.append(f"\n## {SECTION_TITLE[section]}\n")
            sections_seen.add(section)

        md_path = IMG / section / f"{fid}.md"
        meta = parse_yaml(md_path.read_text(encoding="utf-8")) if md_path.exists() else {}
        is_placeholder = meta.get("detail_status", "") == "generic_placeholder"
        anchors = folio_anchors(fid, corpus, pmi_df)
        try:
            prose = SECTION_FN[section](meta, anchors, rng)
        except Exception:
            prose = "(이 페이지의 데이터는 빈약하거나 누락되었다.)"

        flag = " ⓟ" if is_placeholder else ""
        lang = (frow.get("currier_lang") or "").strip()
        lang_tag = f" · {lang}" if lang in ("A", "B") else ""

        out.append(f"### {fid}{flag}{lang_tag}\n\n{prose}\n")

    # 후기
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
    print(f"   Length: {len(book):,} chars  ({len(book.splitlines()):,} lines)")
    print(f"   Pages covered: {len(folio_meta)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

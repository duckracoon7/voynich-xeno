"""
Phase 7 — 카테고리 사전 + 이미지 앵커 후보

빈도 ≥ 5 토큰을 대상으로:
  (a) 임베딩 K-means 클러스터링 (자동 카테고리 라벨)
  (b) 이미지 YAML 특성과 co-occurrence (Pointwise Mutual Information)
  (c) 클러스터별 대표 시각 특성 산출 → 카테고리 의미 후보
  (d) 토큰별 후보 의미 + 신뢰도 점수

산출:
  artifacts/dictionary/dictionary.csv (사람용 사전)
  artifacts/dictionary/dictionary.parquet
  artifacts/dictionary/cluster_categories.json
  artifacts/dictionary/anchor_pairs.csv (이미지-앵커된 후보 매핑)
"""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
EMB = ROOT / "artifacts" / "embeddings"
DIC = ROOT / "artifacts" / "dictionary"
IMG = ROOT / "image_descriptions"
DIC.mkdir(parents=True, exist_ok=True)

MAIN_MODEL = "w2v_ALL_256"
N_CLUSTERS = 30  # 토큰 클러스터 수 (휴리스틱: vocab/50)
MIN_FREQ = 5

# Phase 5와 동일한 비전 특성
VISION_FIELDS = [
    "n_text_blocks", "n_visual_text_columns", "n_distinct_objects",
    "n_labels", "n_colors_used", "n_decorative_motifs",
    "has_circular_structure", "has_radial_symmetry", "has_human_figure",
    "has_container", "has_water", "has_sun_face", "has_moon_face",
    "has_marginal_annotation", "has_spiral", "has_T_O_diagram",
    "has_central_star", "has_central_object", "has_star_motif",
    "fragments_are_whole_plants", "n_stars", "n_concentric_rings",
    "n_human_figures", "n_containers", "n_plant_fragments", "n_rows",
    "n_paragraphs", "n_petals", "n_rays", "n_leaves_visible",
    "n_flowers_visible", "branching_depth", "n_red_stars",
    "n_tailed_stars", "n_nymphs", "n_pools", "n_pipes",
    "spiral_turns", "n_beads", "n_rays_or_petals",
]


def parse_yaml_block(md_text: str) -> dict:
    blocks = re.findall(r"```yaml\s*\n(.*?)\n```", md_text, re.DOTALL)
    if not blocks:
        return {}
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
                continue
            else:
                try:
                    flat[key] = float(val)
                except ValueError:
                    continue
    return flat


def folio_features(folio_id: str, section: str) -> dict:
    md = IMG / section / f"{folio_id}.md"
    if not md.exists():
        return {}
    return parse_yaml_block(md.read_text(encoding="utf-8"))


def main() -> int:
    tokens_df = pd.read_parquet(COR / "tokens.parquet")
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")
    profile = pd.read_parquet(DIC / "token_profile.parquet")
    kv = KeyedVectors.load(str(EMB / f"{MAIN_MODEL}.kv"))

    # --- 1. 빈도 필터 + 임베딩 추출 ---
    keep = profile["freq"] >= MIN_FREQ
    tokens = profile.loc[keep, "token"].tolist()
    tokens = [t for t in tokens if t in kv]
    print(f"Tokens with freq>={MIN_FREQ} and in vocab: {len(tokens)}")

    X = np.stack([kv[t] for t in tokens])

    # --- 2. K-means 클러스터링 ---
    km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=20)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)
    print(f"Silhouette (k={N_CLUSTERS}): {sil:.3f}")

    cluster_df = pd.DataFrame({"token": tokens, "cluster": labels})

    # --- 3. 폴리오 특성 사전 구축 ---
    folio_feats: dict[str, dict] = {}
    for _, frow in folio_meta.iterrows():
        feats = folio_features(frow["folio_id"], frow["section"])
        feats["__section__"] = frow["section"]
        folio_feats[frow["folio_id"]] = feats

    # --- 4. 토큰 ↔ 비전 특성 PMI ---
    # P(feature_active | token) vs P(feature_active)
    # PMI = log( P(token, feat) / (P(token) × P(feat)) )
    token_folios = tokens_df.groupby("token")["folio_id"].apply(set).to_dict()
    n_folios_total = len(folio_meta)

    # 비전 특성별 활성 폴리오 (값 > 0)
    feat_active: dict[str, set[str]] = {f: set() for f in VISION_FIELDS}
    feat_value_sum: dict[str, float] = {f: 0.0 for f in VISION_FIELDS}
    for fid, feats in folio_feats.items():
        for f in VISION_FIELDS:
            v = feats.get(f, 0.0)
            if v and v > 0:
                feat_active[f].add(fid)
                feat_value_sum[f] += float(v)

    # 토큰 ↔ 특성 PMI 매트릭스
    pmi_rows = []
    for tok in tokens:
        tok_folios = token_folios.get(tok, set())
        n_t = len(tok_folios)
        if n_t == 0:
            continue
        for feat, feat_set in feat_active.items():
            n_f = len(feat_set)
            n_tf = len(tok_folios & feat_set)
            if n_f == 0 or n_tf == 0:
                continue
            p_t = n_t / n_folios_total
            p_f = n_f / n_folios_total
            p_tf = n_tf / n_folios_total
            pmi = np.log2(p_tf / (p_t * p_f))
            # 보조: 정규화 PMI (NPMI) ∈ [-1, 1]
            npmi = pmi / -np.log2(p_tf) if p_tf < 1 else 0.0
            pmi_rows.append({
                "token": tok,
                "feature": feat,
                "n_token_folios": n_t,
                "n_feature_folios": n_f,
                "n_joint": n_tf,
                "pmi": float(pmi),
                "npmi": float(npmi),
                "support": n_tf,
            })
    pmi_df = pd.DataFrame(pmi_rows)
    pmi_df.to_parquet(DIC / "token_feature_pmi.parquet", index=False)

    # --- 5. 토큰별 top-3 anchor 후보 ---
    pmi_df["score"] = pmi_df["npmi"] * np.sqrt(pmi_df["support"])
    top_per_token = (
        pmi_df.sort_values(["token", "score"], ascending=[True, False])
        .groupby("token")
        .head(3)
        .reset_index(drop=True)
    )

    anchor_lines: list[dict] = []
    for tok, grp in top_per_token.groupby("token"):
        cands = []
        for _, r in grp.iterrows():
            if r["score"] > 0:
                cands.append(f"{r['feature']}(npmi={r['npmi']:+.2f}, n={r['n_joint']})")
        anchor_lines.append({
            "token": tok,
            "top_anchors": " | ".join(cands) if cands else "(no positive PMI anchor)",
        })
    anchor_df = pd.DataFrame(anchor_lines)
    anchor_df.to_csv(DIC / "anchor_pairs.csv", index=False)

    # --- 6. 클러스터별 대표 카테고리 ---
    # 각 클러스터에서 자주 언급되는 비전 특성 + 도미넌트 섹션 식별
    cluster_meta: dict[int, dict] = {}
    for c in range(N_CLUSTERS):
        cl_tokens = cluster_df[cluster_df["cluster"] == c]["token"].tolist()
        if not cl_tokens:
            continue
        # 클러스터 토큰들의 평균 PMI per feature
        sub = pmi_df[pmi_df["token"].isin(cl_tokens)]
        if sub.empty:
            top_feats = []
        else:
            mean_npmi = sub.groupby("feature")["npmi"].mean().sort_values(ascending=False)
            top_feats = mean_npmi.head(3).index.tolist()

        sub_prof = profile[profile["token"].isin(cl_tokens)]
        sec_dist = sub_prof["dominant_section"].value_counts(normalize=True).head(2).to_dict()
        in_label_avg = float(sub_prof["in_label_pct"].mean())
        cluster_meta[c] = {
            "n_tokens": len(cl_tokens),
            "examples": cl_tokens[:8],
            "top_visual_features": top_feats,
            "dominant_sections": sec_dist,
            "label_dominance": round(in_label_avg, 3),
        }

    (DIC / "cluster_categories.json").write_text(
        json.dumps(cluster_meta, ensure_ascii=False, indent=2)
    )

    # --- 7. 통합 사전 ---
    profile_subset = profile[profile["token"].isin(tokens)].copy()
    profile_subset = profile_subset.merge(cluster_df, on="token", how="left")
    profile_subset = profile_subset.merge(anchor_df, on="token", how="left")
    profile_subset = profile_subset.sort_values("freq", ascending=False)

    # 카테고리 인간 라벨 생성
    def cluster_label(c):
        meta = cluster_meta.get(int(c), {})
        secs = meta.get("dominant_sections", {})
        feats = meta.get("top_visual_features", [])
        label_pct = meta.get("label_dominance", 0)
        sec_str = "/".join(list(secs.keys())[:2]) if secs else "?"
        feat_str = "+".join(feats[:2]) if feats else "(no visual signal)"
        role = "label" if label_pct > 0.5 else "body"
        return f"[{role}] {sec_str} | {feat_str}"

    profile_subset["category"] = profile_subset["cluster"].apply(
        lambda c: cluster_label(c) if pd.notna(c) else ""
    )

    profile_subset.to_csv(DIC / "dictionary.csv", index=False)
    profile_subset.to_parquet(DIC / "dictionary.parquet", index=False)

    # 요약
    print("\n=== Phase 7 Dictionary ===")
    print(f"Dictionary entries: {len(profile_subset):,}")
    print(f"Anchor candidates (token-feature pairs with PMI>0): {(pmi_df['pmi']>0).sum():,}")
    print(f"Tokens with at least one positive anchor: "
          f"{anchor_df['top_anchors'].apply(lambda s: 'no positive' not in s).sum():,}")
    print()
    print("Top 15 dictionary entries:")
    cols = ["token", "freq", "n_folios", "in_label_pct", "dominant_section",
            "category", "top_anchors"]
    pd.set_option("display.max_colwidth", 60)
    print(profile_subset[cols].head(15).to_string(index=False))

    print("\n✅ Phase 7 dictionary complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

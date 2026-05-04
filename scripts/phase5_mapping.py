"""
Phase 5 — 이미지-텍스트 매핑 (간이 버전)

DINOv2 비전 인코더 대신 *우리 이미지 관찰 노트의 YAML 정량 요약*을 비전
특성 벡터로 사용. 통제 가능하고 PyTorch 비의존.

전략:
  - 각 폴리오 .md에서 YAML quantitative summary 파싱
  - 표준 수치 필드를 비전 벡터 V_f로 추출
  - 텍스트 벡터 T_f = mean(token embeddings of folio f)
  - 80/20 holdout split
  - Procrustes (직교 정렬) + Linear regression 두 가지 정렬
  - holdout 폴리오에서 T_f → 가장 가까운 V_f' retrieval
  - Recall@1, MRR

귀무가설: 무작위 매핑 (Recall@1 ≈ 1/N_holdout)
채택 기준: holdout Recall@1 ≥ 5×random + 두 메서드 합의
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.linear_model import Ridge
from scipy.linalg import orthogonal_procrustes

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
EMB = ROOT / "artifacts" / "embeddings"
IMG = ROOT / "image_descriptions"
OUT = ROOT / "artifacts" / "mapping"
OUT.mkdir(parents=True, exist_ok=True)

MAIN_MODEL = "w2v_ALL_256"

# 비전 특성으로 사용할 YAML 필드 (표준화된 수치)
VISION_FIELDS = [
    "n_text_blocks",
    "n_visual_text_columns",
    "n_distinct_objects",
    "n_labels",
    "n_colors_used",
    "n_decorative_motifs",
    "has_circular_structure",
    "has_radial_symmetry",
    "has_human_figure",
    "has_container",
    "has_water",
    "has_sun_face",
    "has_moon_face",
    "has_marginal_annotation",
    "has_spiral",
    "has_T_O_diagram",
    "has_central_star",
    "has_central_object",
    "has_star_motif",
    "fragments_are_whole_plants",
    # 섹션-특화 features
    "n_stars",
    "n_concentric_rings",
    "n_human_figures",
    "n_containers",
    "n_plant_fragments",
    "n_rows",
    "n_paragraphs",
    "n_petals",
    "n_rays",
    "n_leaves_visible",
    "n_flowers_visible",
    "branching_depth",
    "n_red_stars",
    "n_tailed_stars",
    "n_nymphs",
    "n_pools",
    "n_pipes",
    "spiral_turns",
    "n_beads",
    "n_rays_or_petals",
]


def parse_yaml_block(md_text: str) -> dict:
    """이미지 .md의 YAML quantitative summary 파싱.

    YAML 블록은 ```yaml ... ``` 안에 있음. plant_features 등 nested도 처리.
    """
    # ```yaml ... ``` 블록 찾기 (여러 개일 수 있음)
    blocks = re.findall(r"```yaml\s*\n(.*?)\n```", md_text, re.DOTALL)
    if not blocks:
        return {}

    flat: dict = {}
    for block in blocks:
        # 매우 단순한 YAML 파서 — key: value 형태만
        for line in block.splitlines():
            line = line.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            # nested (들여쓰기) 무시하고 키 평탄화
            m = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if not m:
                continue
            key, val = m.group(1), m.group(2).strip()
            if not val or val.startswith(("[", "{")):  # list/object/empty: skip
                continue
            # 인라인 코멘트 제거
            val = val.split("#")[0].strip()
            # 값 파싱
            if val.lower() in ("true", "false"):
                flat[key] = 1.0 if val.lower() == "true" else 0.0
            elif val.lower() in ("null", "none", "___"):
                continue
            elif val.startswith('"') and val.endswith('"'):
                continue  # 문자열 무시
            else:
                try:
                    flat[key] = float(val)
                except ValueError:
                    continue
    return flat


def vision_vector(folio_id: str, section: str) -> np.ndarray | None:
    """폴리오의 비전 벡터 추출."""
    md = IMG / section / f"{folio_id}.md"
    if not md.exists():
        return None
    parsed = parse_yaml_block(md.read_text(encoding="utf-8"))
    vec = []
    for f in VISION_FIELDS:
        v = parsed.get(f, 0.0)
        vec.append(v)
    return np.array(vec, dtype=np.float32)


def folio_text_vector(
    folio_id: str,
    corpus_df: pd.DataFrame,
    kv: KeyedVectors,
) -> np.ndarray | None:
    """폴리오 토큰 임베딩 평균."""
    folio = corpus_df[corpus_df["folio_id"] == folio_id]
    vecs = []
    for _, row in folio.iterrows():
        eva = row["eva_text"]
        if not eva:
            continue
        words = [w for w in eva.replace("<->", ".").replace(",", ".").split(".") if w]
        for w in words:
            if w in kv:
                vecs.append(kv[w])
    if not vecs:
        return None
    return np.mean(np.stack(vecs), axis=0)


def build_pairs(
    corpus_df: pd.DataFrame,
    kv: KeyedVectors,
    folio_meta: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """모든 폴리오의 (vision, text) 페어 구축."""
    V_list, T_list, ids = [], [], []
    for _, frow in folio_meta.iterrows():
        fid, section = frow["folio_id"], frow["section"]
        V = vision_vector(fid, section)
        T = folio_text_vector(fid, corpus_df, kv)
        if V is None or T is None:
            continue
        V_list.append(V)
        T_list.append(T)
        ids.append(fid)
    return np.stack(V_list), np.stack(T_list), ids


def standardize(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True) + 1e-9
    return (X - mu) / sd, mu, sd


def evaluate_retrieval(
    T_test: np.ndarray, V_test: np.ndarray
) -> dict:
    """T (정렬된) → V 가장 가까운 retrieval. Recall@1, @5, MRR."""
    # 코사인 유사도 (단위벡터화 후 dot product)
    T_n = T_test / (np.linalg.norm(T_test, axis=1, keepdims=True) + 1e-9)
    V_n = V_test / (np.linalg.norm(V_test, axis=1, keepdims=True) + 1e-9)
    sim = T_n @ V_n.T  # [n, n]
    n = sim.shape[0]
    ranks = []
    for i in range(n):
        order = np.argsort(-sim[i])
        rank = int(np.where(order == i)[0][0])
        ranks.append(rank)
    ranks = np.array(ranks)
    return {
        "n_test": int(n),
        "recall_at_1": float(np.mean(ranks == 0)),
        "recall_at_5": float(np.mean(ranks < 5)),
        "recall_at_10": float(np.mean(ranks < 10)),
        "mrr": float(np.mean(1.0 / (ranks + 1))),
        "random_baseline_at_1": float(1.0 / n),
    }


def main() -> int:
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")
    corpus = pd.read_parquet(COR / "corpus.parquet")
    kv = KeyedVectors.load(str(EMB / f"{MAIN_MODEL}.kv"))

    V_all, T_all, ids = build_pairs(corpus, kv, folio_meta)
    print(f"Total folios with both vectors: {len(ids)}")

    # 80/20 split
    rng = np.random.default_rng(42)
    idx = np.arange(len(ids))
    rng.shuffle(idx)
    n_train = int(len(idx) * 0.8)
    tr, te = idx[:n_train], idx[n_train:]

    V_tr, V_te = V_all[tr], V_all[te]
    T_tr, T_te = T_all[tr], T_all[te]

    # 표준화 (train 통계로 test 표준화)
    V_tr_s, v_mu, v_sd = standardize(V_tr)
    V_te_s = (V_te - v_mu) / v_sd
    T_tr_s, t_mu, t_sd = standardize(T_tr)
    T_te_s = (T_te - t_mu) / t_sd

    # ---- 메서드 1: Procrustes (직교 정렬, V를 T 차원으로 패딩 후) ----
    # T (n_train, 256), V (n_train, k). V를 패딩으로 256차원 매칭.
    pad = T_tr_s.shape[1] - V_tr_s.shape[1]
    V_tr_pad = np.hstack([V_tr_s, np.zeros((V_tr_s.shape[0], pad), dtype=V_tr_s.dtype)])
    V_te_pad = np.hstack([V_te_s, np.zeros((V_te_s.shape[0], pad), dtype=V_te_s.dtype)])
    R, _ = orthogonal_procrustes(V_tr_pad, T_tr_s)
    V_te_proc = V_te_pad @ R
    res_proc = evaluate_retrieval(T_te_s, V_te_proc)

    # ---- 메서드 2: Ridge regression (T 공간으로 학습) ----
    ridge = Ridge(alpha=1.0)
    ridge.fit(V_tr_s, T_tr_s)
    V_te_ridge = ridge.predict(V_te_s)
    res_ridge = evaluate_retrieval(T_te_s, V_te_ridge)

    # ---- 합의 ----
    threshold_factor = 5.0
    rand = res_proc["random_baseline_at_1"]
    proc_pass = res_proc["recall_at_1"] >= threshold_factor * rand
    ridge_pass = res_ridge["recall_at_1"] >= threshold_factor * rand
    consensus = proc_pass and ridge_pass

    summary = {
        "main_model": MAIN_MODEL,
        "n_total_folios": len(ids),
        "n_train": int(len(tr)),
        "n_test": int(len(te)),
        "vision_feature_dim": V_all.shape[1],
        "text_embed_dim": T_all.shape[1],
        "method_1_procrustes": res_proc,
        "method_2_ridge": res_ridge,
        "threshold": f"recall@1 >= {threshold_factor} × random ({threshold_factor * rand:.4f})",
        "method_1_passed": bool(proc_pass),
        "method_2_passed": bool(ridge_pass),
        "consensus": bool(consensus),
    }

    (OUT / "phase5_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )

    print()
    print("=== Phase 5 Image-Text Mapping ===")
    print(f"Train/Test: {len(tr)}/{len(te)}")
    print(f"Vision dim: {V_all.shape[1]}  |  Text dim: {T_all.shape[1]}")
    print()
    print("Method 1 — Procrustes (orthogonal):")
    print(f"  Recall@1  = {res_proc['recall_at_1']:.4f}  (random: {rand:.4f})")
    print(f"  Recall@5  = {res_proc['recall_at_5']:.4f}")
    print(f"  Recall@10 = {res_proc['recall_at_10']:.4f}")
    print(f"  MRR       = {res_proc['mrr']:.4f}")
    print()
    print("Method 2 — Ridge regression:")
    print(f"  Recall@1  = {res_ridge['recall_at_1']:.4f}  (random: {rand:.4f})")
    print(f"  Recall@5  = {res_ridge['recall_at_5']:.4f}")
    print(f"  Recall@10 = {res_ridge['recall_at_10']:.4f}")
    print(f"  MRR       = {res_ridge['mrr']:.4f}")
    print()
    print(f"Threshold: Recall@1 >= 5×random ({threshold_factor*rand:.4f})")
    print(f"  Procrustes passed: {proc_pass}")
    print(f"  Ridge passed:      {ridge_pass}")
    print(f"  Consensus:         {consensus}")
    print()
    if consensus:
        print("✅ Phase 5 mapping CONSENSUS — image-text mapping signal detected")
        print("   (단, vision features는 인간 작성 YAML이라 Phase 5의 *상한선*만 평가)")
    elif proc_pass or ridge_pass:
        print("⚠️  Phase 5 partial signal (one method only)")
    else:
        print("❌ Phase 5 mapping FAILED — no signal above random baseline")

    return 0 if consensus else 1


if __name__ == "__main__":
    sys.exit(main())

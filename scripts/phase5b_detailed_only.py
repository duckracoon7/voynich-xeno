"""
Phase 5b — 상세 관찰 폴리오만으로 매핑 재검증

124개 herbal placeholder가 동일 vision vector를 가져 retrieval 변별력을
떨어뜨리는 효과를 분리하기 위해, *generic placeholder를 제외한 102개*
상세 관찰 폴리오로만 평가.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.linear_model import Ridge
from scipy.linalg import orthogonal_procrustes

sys.path.insert(0, str(Path(__file__).parent))
from phase5_mapping import (
    parse_yaml_block,
    vision_vector,
    folio_text_vector,
    standardize,
    evaluate_retrieval,
    MAIN_MODEL,
    COR,
    EMB,
    IMG,
)

OUT = Path(__file__).resolve().parent.parent / "artifacts" / "mapping"


def is_detailed(folio_id: str, section: str) -> bool:
    """generic_placeholder 플래그가 없는 폴리오만 detailed."""
    md = IMG / section / f"{folio_id}.md"
    if not md.exists():
        return False
    text = md.read_text(encoding="utf-8")
    return 'detail_status: "generic_placeholder"' not in text


def main() -> int:
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")
    corpus = pd.read_parquet(COR / "corpus.parquet")
    kv = KeyedVectors.load(str(EMB / f"{MAIN_MODEL}.kv"))

    V_list, T_list, ids = [], [], []
    for _, frow in folio_meta.iterrows():
        fid, section = frow["folio_id"], frow["section"]
        if not is_detailed(fid, section):
            continue
        V = vision_vector(fid, section)
        T = folio_text_vector(fid, corpus, kv)
        if V is None or T is None:
            continue
        V_list.append(V)
        T_list.append(T)
        ids.append(fid)

    V_all = np.stack(V_list)
    T_all = np.stack(T_list)
    print(f"Detailed-only folios: {len(ids)}")

    rng = np.random.default_rng(42)
    idx = np.arange(len(ids))
    rng.shuffle(idx)
    n_train = int(len(idx) * 0.8)
    tr, te = idx[:n_train], idx[n_train:]

    V_tr, V_te = V_all[tr], V_all[te]
    T_tr, T_te = T_all[tr], T_all[te]

    V_tr_s, v_mu, v_sd = standardize(V_tr)
    V_te_s = (V_te - v_mu) / v_sd
    T_tr_s, t_mu, t_sd = standardize(T_tr)
    T_te_s = (T_te - t_mu) / t_sd

    pad = T_tr_s.shape[1] - V_tr_s.shape[1]
    V_tr_pad = np.hstack([V_tr_s, np.zeros((V_tr_s.shape[0], pad), dtype=V_tr_s.dtype)])
    V_te_pad = np.hstack([V_te_s, np.zeros((V_te_s.shape[0], pad), dtype=V_te_s.dtype)])
    R, _ = orthogonal_procrustes(V_tr_pad, T_tr_s)
    V_te_proc = V_te_pad @ R
    res_proc = evaluate_retrieval(T_te_s, V_te_proc)

    ridge = Ridge(alpha=1.0)
    ridge.fit(V_tr_s, T_tr_s)
    V_te_ridge = ridge.predict(V_te_s)
    res_ridge = evaluate_retrieval(T_te_s, V_te_ridge)

    rand = res_proc["random_baseline_at_1"]
    threshold_factor = 5.0
    proc_pass = res_proc["recall_at_1"] >= threshold_factor * rand
    ridge_pass = res_ridge["recall_at_1"] >= threshold_factor * rand
    consensus = proc_pass and ridge_pass

    summary = {
        "scope": "detailed observations only (excludes 124 herbal placeholders)",
        "n_total_folios": len(ids),
        "n_train": int(len(tr)),
        "n_test": int(len(te)),
        "method_1_procrustes": res_proc,
        "method_2_ridge": res_ridge,
        "threshold": f"recall@1 >= {threshold_factor} × random ({threshold_factor * rand:.4f})",
        "method_1_passed": bool(proc_pass),
        "method_2_passed": bool(ridge_pass),
        "consensus": bool(consensus),
    }

    (OUT / "phase5b_detailed_only_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )

    print()
    print("=== Phase 5b Detailed-Only Mapping ===")
    print(f"Train/Test: {len(tr)}/{len(te)}")
    print()
    print("Method 1 — Procrustes:")
    print(f"  Recall@1={res_proc['recall_at_1']:.4f}  @5={res_proc['recall_at_5']:.4f}  "
          f"@10={res_proc['recall_at_10']:.4f}  MRR={res_proc['mrr']:.4f}")
    print("Method 2 — Ridge:")
    print(f"  Recall@1={res_ridge['recall_at_1']:.4f}  @5={res_ridge['recall_at_5']:.4f}  "
          f"@10={res_ridge['recall_at_10']:.4f}  MRR={res_ridge['mrr']:.4f}")
    print()
    print(f"Random baseline@1: {rand:.4f}")
    print(f"Threshold (5×): {threshold_factor*rand:.4f}")
    print(f"Procrustes pass: {proc_pass} | Ridge pass: {ridge_pass} | Consensus: {consensus}")
    return 0 if consensus else 2


if __name__ == "__main__":
    sys.exit(main())

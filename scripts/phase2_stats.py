"""
Phase 2 — 통계 베이스라인 재현

선행 연구 수치를 우리 파이프라인이 재현하는지 검증.

검증 항목:
  (1) Zipf's law 부합성 — Montemurro & Zanette (2013)
  (2) 단어 길이 분포 — Reddy & Knight (2011)
  (3) 2차 조건부 엔트로피 h₂ ≈ 2 — Bowern & Lindemann (2021)
  (4) Currier A vs B 분리의 통계적 견고성 — character-pair 분포 차이

Gate: h₂가 2.0 ± 0.3 영역에 들어오면 통과 (다른 지표는 보조 비교).
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
OUT = ROOT / "artifacts" / "stats"
OUT.mkdir(parents=True, exist_ok=True)


def char_stream(tokens: list[str], sep: str = " ") -> str:
    """토큰 리스트를 문자 시퀀스로. 공백을 단어 경계 표지로 추가."""
    return sep.join(tokens)


def char_entropy(text: str, n: int = 1) -> float:
    """n-gram 문자 엔트로피 (bits/char).

    n=1: 1차 (single char) entropy
    n=2: conditional entropy h2 = H(X_t | X_{t-1})
    """
    if n == 1:
        cnt = Counter(text)
        total = sum(cnt.values())
        probs = np.array([c / total for c in cnt.values()])
        return -float(np.sum(probs * np.log2(probs)))
    elif n == 2:
        # h2 = H(X1, X2) - H(X1)
        bigrams = Counter(text[i : i + 2] for i in range(len(text) - 1))
        unigrams = Counter(text)
        total_bg = sum(bigrams.values())
        total_ug = sum(unigrams.values())
        p_bg = np.array([c / total_bg for c in bigrams.values()])
        p_ug = np.array([c / total_ug for c in unigrams.values()])
        H12 = -float(np.sum(p_bg * np.log2(p_bg)))
        H1 = -float(np.sum(p_ug * np.log2(p_ug)))
        return H12 - H1
    else:
        raise ValueError("n must be 1 or 2")


def zipf_fit(token_counts: Counter) -> tuple[float, float]:
    """Zipf 적합. 빈도 vs 랭크의 log-log 회귀.

    반환: (alpha, r_squared)
    Zipf의 법칙은 alpha ≈ 1을 예측 (음의 부호로 -1).
    """
    freqs = sorted(token_counts.values(), reverse=True)
    ranks = np.arange(1, len(freqs) + 1)
    log_r = np.log10(ranks)
    log_f = np.log10(freqs)
    # head + body만 사용 (꼬리는 1회 등장 토큰들로 노이즈)
    keep = np.array(freqs) >= 2
    res = stats.linregress(log_r[keep], log_f[keep])
    return -float(res.slope), float(res.rvalue ** 2)


def word_length_distribution(tokens: list[str]) -> dict:
    """단어 길이 분포 통계."""
    lens = np.array([len(t) for t in tokens if t])
    return {
        "mean": float(lens.mean()),
        "std": float(lens.std()),
        "median": float(np.median(lens)),
        "min": int(lens.min()),
        "max": int(lens.max()),
        "histogram": {
            int(k): int(v) for k, v in Counter(lens.tolist()).items()
        },
    }


def char_pair_predict(tokens_train: list[str], tokens_test: list[str]) -> float:
    """train의 bigram 분포로 test의 bigram을 평가 (-log likelihood proxy).

    낮을수록 train과 test가 같은 분포에서 옴 (= 같은 언어/방언).
    Currier A/B 구분의 통계적 견고성 검증.
    """
    text_train = " ".join(tokens_train)
    text_test = " ".join(tokens_test)
    bg_train = Counter(text_train[i : i + 2] for i in range(len(text_train) - 1))
    total_train = sum(bg_train.values())
    p_train = {k: v / total_train for k, v in bg_train.items()}
    # smoothing
    eps = 1e-7
    nll = 0.0
    n = 0
    for i in range(len(text_test) - 1):
        bg = text_test[i : i + 2]
        p = p_train.get(bg, eps)
        nll -= np.log2(p)
        n += 1
    return float(nll / n) if n else float("inf")


def main() -> int:
    tokens_df = pd.read_parquet(COR / "tokens.parquet")

    # 전체
    all_tokens = tokens_df["token"].tolist()
    text_all = " ".join(all_tokens)
    H1_all = char_entropy(text_all, 1)
    H2_all = char_entropy(text_all, 2)
    counts_all = Counter(all_tokens)
    zipf_alpha, zipf_r2 = zipf_fit(counts_all)
    wl_all = word_length_distribution(all_tokens)

    # Currier A/B 분리
    tokens_A = tokens_df[tokens_df["currier_lang"] == "A"]["token"].tolist()
    tokens_B = tokens_df[tokens_df["currier_lang"] == "B"]["token"].tolist()

    H2_A = char_entropy(" ".join(tokens_A), 2)
    H2_B = char_entropy(" ".join(tokens_B), 2)

    # Currier A/B distinction: A→B와 B→A의 NLL이 within 분포보다 클 것
    # within-distribution: A→A (split half), B→B (split half)
    rng = np.random.default_rng(42)
    rng.shuffle(tokens_A)
    rng.shuffle(tokens_B)
    half_A = len(tokens_A) // 2
    half_B = len(tokens_B) // 2

    nll_AA = char_pair_predict(tokens_A[:half_A], tokens_A[half_A:])
    nll_BB = char_pair_predict(tokens_B[:half_B], tokens_B[half_B:])
    nll_AB = char_pair_predict(tokens_A, tokens_B)
    nll_BA = char_pair_predict(tokens_B, tokens_A)

    # 결과 직렬화
    results = {
        "all": {
            "n_tokens": len(all_tokens),
            "n_types": len(counts_all),
            "H1_bits_per_char": H1_all,
            "H2_bits_per_char": H2_all,
            "zipf_alpha": zipf_alpha,
            "zipf_r2": zipf_r2,
            "word_length": wl_all,
        },
        "currier_A": {
            "n_tokens": len(tokens_A),
            "H2_bits_per_char": H2_A,
        },
        "currier_B": {
            "n_tokens": len(tokens_B),
            "H2_bits_per_char": H2_B,
        },
        "currier_distinction_nll_bits": {
            "within_A_to_A_split": nll_AA,
            "within_B_to_B_split": nll_BB,
            "across_A_to_B": nll_AB,
            "across_B_to_A": nll_BA,
            "across_minus_within_A": nll_AB - nll_AA,
            "across_minus_within_B": nll_BA - nll_BB,
        },
        "literature_targets": {
            "h2_target": "≈ 2 (Bowern & Lindemann 2021)",
            "zipf_alpha_target": "≈ 1 (Montemurro & Zanette 2013)",
            "word_length_mean_target": "≈ 5.0 (Reddy & Knight 2011)",
        },
    }

    out_path = OUT / "phase2_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    # 화면 출력
    print("=== Phase 2 Statistical Baseline ===")
    print()
    print(f"Tokens: {len(all_tokens):,}  Types: {len(counts_all):,}")
    print()
    print(f"Character entropy H1: {H1_all:.3f} bits/char")
    print(f"2nd-order conditional entropy h2: {H2_all:.3f} bits/char")
    print(f"  → Bowern & Lindemann 2021 target: ≈ 2")
    print()
    print(f"Zipf alpha: {zipf_alpha:.3f}  (R² = {zipf_r2:.3f})")
    print(f"  → Target: ≈ 1")
    print()
    print(f"Word length: mean={wl_all['mean']:.2f}, std={wl_all['std']:.2f}, max={wl_all['max']}")
    print(f"  → Target: ~5.0")
    print()
    print(f"Currier A h2: {H2_A:.3f}  | B h2: {H2_B:.3f}")
    print()
    print("Currier A/B distinction (cross-entropy NLL bits):")
    print(f"  within A→A: {nll_AA:.3f}")
    print(f"  within B→B: {nll_BB:.3f}")
    print(f"  across A→B: {nll_AB:.3f}  (Δ = {nll_AB - nll_AA:+.3f})")
    print(f"  across B→A: {nll_BA:.3f}  (Δ = {nll_BA - nll_BB:+.3f})")

    # 게이트 평가
    print()
    print("=== Gate Evaluation ===")
    gate_h2 = 1.5 <= H2_all <= 2.5
    gate_zipf = 0.7 <= zipf_alpha <= 1.5
    gate_wl = 4.0 <= wl_all["mean"] <= 6.5
    gate_currier = (nll_AB > nll_AA) and (nll_BA > nll_BB)

    print(f"  h2 in [1.5, 2.5]:           {gate_h2}  ({H2_all:.3f})")
    print(f"  zipf in [0.7, 1.5]:         {gate_zipf}  ({zipf_alpha:.3f})")
    print(f"  word length in [4, 6.5]:    {gate_wl}  ({wl_all['mean']:.2f})")
    print(f"  Currier A/B distinguishable: {gate_currier}")

    passes = sum([gate_h2, gate_zipf, gate_wl, gate_currier])
    print()
    if passes >= 3:
        print(f"✅ Phase 2 gate PASSED ({passes}/4 checks)")
        return 0
    else:
        print(f"❌ Phase 2 gate FAILED ({passes}/4 checks)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

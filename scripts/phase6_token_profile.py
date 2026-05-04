"""
Phase 6 — 단어별 분포·역할 프로파일

각 EVA 토큰에 대해:
  - 빈도 / 어떤 섹션에 등장 / 어떤 locator에 등장 (label vs body)
  - Currier A vs B 비율
  - prefix/midfix/suffix 위치 통계 (Bowern & Lindemann 2021)
  - hapax 여부
  - co-occurring 토큰 (같은 라인 내)

산출:
  artifacts/dictionary/token_profile.parquet
  artifacts/dictionary/token_profile.csv (사람이 보기 쉬운 형태)
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
OUT = ROOT / "artifacts" / "dictionary"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    tokens_df = pd.read_parquet(COR / "tokens.parquet")
    folio_meta = pd.read_parquet(COR / "folio_meta.parquet")

    print(f"Total token instances: {len(tokens_df):,}")
    print(f"Unique types: {tokens_df['token'].nunique():,}")

    # --- 토큰별 기본 통계 ---
    tok_freq = tokens_df["token"].value_counts()

    # 섹션 분포 (정규화)
    sec_counts = tokens_df.groupby(["token", "section"]).size().unstack(fill_value=0)
    sec_dist = sec_counts.div(sec_counts.sum(axis=1), axis=0)

    # locator 분포 (정규화) — label vs body 핵심
    loc_counts = tokens_df.groupby(["token", "locator"]).size().unstack(fill_value=0)
    loc_dist_simple = pd.DataFrame({
        "in_label_pct": (
            tokens_df.assign(is_lab=tokens_df["is_label"])
            .groupby("token")["is_lab"].mean()
        ),
        "in_paragraph_pct": (
            tokens_df.assign(is_par=tokens_df["is_paragraph"])
            .groupby("token")["is_par"].mean()
        ),
    })

    # Currier A/B 비율
    cur = tokens_df.groupby(["token", "currier_lang"]).size().unstack(fill_value=0)
    cur["A_pct"] = cur.get("A", 0) / cur.sum(axis=1).replace(0, 1)
    cur["B_pct"] = cur.get("B", 0) / cur.sum(axis=1).replace(0, 1)

    # 폴리오 분포 — 얼마나 많은 폴리오에 등장하는가 (DF, document frequency)
    folio_set = tokens_df.groupby("token")["folio_id"].nunique()

    # 토큰 길이 통계
    lens = pd.Series([len(t) for t in tok_freq.index], index=tok_freq.index)

    # prefix-midfix-suffix 위치 (단어 내 첫 글자 / 마지막 글자 분포)
    # Bowern & Lindemann의 3-필드 구조 분석
    starts = pd.Series([t[0] if t else "" for t in tok_freq.index], index=tok_freq.index)
    ends = pd.Series([t[-1] if t else "" for t in tok_freq.index], index=tok_freq.index)

    # 통합
    profile = pd.DataFrame({
        "token": tok_freq.index,
        "freq": tok_freq.values,
        "n_folios": folio_set.reindex(tok_freq.index).values,
        "length": lens.reindex(tok_freq.index).values,
        "first_char": starts.reindex(tok_freq.index).values,
        "last_char": ends.reindex(tok_freq.index).values,
        "in_label_pct": loc_dist_simple["in_label_pct"].reindex(tok_freq.index).values,
        "in_paragraph_pct": loc_dist_simple["in_paragraph_pct"].reindex(tok_freq.index).values,
        "A_pct": cur["A_pct"].reindex(tok_freq.index).fillna(0).values,
        "B_pct": cur["B_pct"].reindex(tok_freq.index).fillna(0).values,
    })

    # 우세 섹션
    sec_argmax = sec_dist.idxmax(axis=1)
    sec_max = sec_dist.max(axis=1)
    profile["dominant_section"] = sec_argmax.reindex(tok_freq.index).values
    profile["dominant_section_pct"] = sec_max.reindex(tok_freq.index).values

    # hapax 플래그
    profile["is_hapax"] = profile["freq"] == 1

    # 의미 추정에 가장 정보가 풍부한 토큰: high freq, narrow section, narrow locator
    profile["specificity"] = profile["dominant_section_pct"] * np.where(
        profile["in_label_pct"] > 0.5, 2.0, 1.0
    )

    # 정렬·저장
    profile = profile.sort_values("freq", ascending=False).reset_index(drop=True)

    profile.to_parquet(OUT / "token_profile.parquet", index=False)
    profile.to_csv(OUT / "token_profile.csv", index=False)

    # 섹션별 토큰 분포 (별도 저장)
    sec_dist.to_parquet(OUT / "token_section_distribution.parquet")
    loc_counts.to_parquet(OUT / "token_locator_counts.parquet")

    # 요약
    print("\n=== Phase 6 Token Profile ===")
    print(f"Total tokens: {len(profile):,}")
    print(f"Hapax (freq=1): {profile['is_hapax'].sum():,}")
    print(f"Frequent (freq>=10): {(profile['freq'] >= 10).sum():,}")
    print(f"Label-dominant (in_label_pct >= 0.7): {(profile['in_label_pct'] >= 0.7).sum():,}")
    print(f"Body-dominant (in_paragraph_pct >= 0.9): {(profile['in_paragraph_pct'] >= 0.9).sum():,}")
    print()
    print("Top 20 tokens:")
    print(profile.head(20).to_string(index=False))
    print()
    print("Section distribution of tokens (dominant):")
    print(profile["dominant_section"].value_counts())

    print("\n✅ Phase 6 token profile complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

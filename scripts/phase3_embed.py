"""
Phase 3 — 임베딩 공간 구축

word2vec, FastText로 Voynichese 분산 표현 학습.

전략:
  - Currier A, B, ALL 각각 별도 학습 (P2 원칙)
  - 차원 128/256/512 비교 (1024는 과적합 위험으로 기각)
  - line 단위가 sentence (단어 순서 보존)
  - min_count=3, window=5

산출:
  artifacts/embeddings/{model}_{lang}_{dim}.kv
  artifacts/embeddings/phase3_models.json (메타데이터)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
import pandas as pd
from gensim.models import Word2Vec, FastText

ROOT = Path(__file__).resolve().parent.parent
COR = ROOT / "artifacts" / "corpus"
OUT = ROOT / "artifacts" / "embeddings"
OUT.mkdir(parents=True, exist_ok=True)


def build_sentences(corpus_df: pd.DataFrame) -> list[list[str]]:
    """라인을 sentence로, 토큰을 단어로."""
    sentences = []
    for _, row in corpus_df.iterrows():
        eva = row["eva_text"]
        if not eva:
            continue
        # 같은 토큰화 로직 (Phase 1)
        # 간단하게 "."로 분리. <-> 와 "," 도 경계.
        s = eva.replace("<->", ".").replace(",", ".")
        words = [w for w in s.split(".") if w]
        if len(words) >= 2:
            sentences.append(words)
    return sentences


def train_one(
    sentences: list[list[str]],
    model_type: str,
    dim: int,
    seed: int = 42,
) -> tuple[object, dict]:
    """단일 모델 학습."""
    t0 = time.time()
    common = dict(
        vector_size=dim,
        window=5,
        min_count=3,
        workers=4,
        epochs=20,
        seed=seed,
    )
    if model_type == "w2v":
        model = Word2Vec(sentences=sentences, sg=1, **common)
    elif model_type == "ft":
        model = FastText(sentences=sentences, sg=1, min_n=2, max_n=4, **common)
    else:
        raise ValueError(model_type)

    elapsed = time.time() - t0
    info = {
        "model_type": model_type,
        "dim": dim,
        "n_sentences": len(sentences),
        "vocab_size": len(model.wv),
        "elapsed_seconds": round(elapsed, 2),
        "config": common,
    }
    return model, info


def main() -> int:
    corpus = pd.read_parquet(COR / "corpus.parquet")

    splits = {
        "ALL": corpus,
        "A": corpus[corpus["currier_lang"] == "A"],
        "B": corpus[corpus["currier_lang"] == "B"],
    }

    all_info: list[dict] = []
    dims = [128, 256, 512]
    types = ["w2v", "ft"]

    for lang, df in splits.items():
        sentences = build_sentences(df)
        print(f"\n=== Currier {lang}: {len(sentences)} sentences ===")
        for model_type in types:
            for dim in dims:
                model, info = train_one(sentences, model_type, dim)
                info["currier_lang"] = lang
                tag = f"{model_type}_{lang}_{dim}"
                model.wv.save(str(OUT / f"{tag}.kv"))
                info["saved"] = f"{tag}.kv"
                all_info.append(info)
                print(
                    f"  {tag}: vocab={info['vocab_size']:,}  "
                    f"elapsed={info['elapsed_seconds']}s"
                )

    (OUT / "phase3_models.json").write_text(
        json.dumps(all_info, ensure_ascii=False, indent=2)
    )

    print("\n=== Summary ===")
    summary_df = pd.DataFrame(all_info)
    print(summary_df.pivot_table(
        index=["model_type", "currier_lang"],
        columns="dim",
        values="vocab_size",
        aggfunc="first",
    ))

    print("\n✅ Phase 3 embedding training complete")
    print(f"   Models saved: {len(all_info)} files in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

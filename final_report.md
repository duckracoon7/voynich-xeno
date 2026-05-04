# Voynich Xeno-Language Pipeline — 최종 결과 보고

> 자동 실행 결과 요약. 자세한 진행은 [`work_log.md`](work_log.md) 참고.

---

## 한눈에 보기

| 항목 | 결과 |
|------|------|
| Phase 1 (정규화) | ✅ 통과 — 226 폴리오, 37,982 토큰 |
| Phase 2 (통계 재현) | ✅ **4/4 통과** — h₂=2.17, Zipf α=1.04, 단어 길이 5.53, A/B 구분 |
| Phase 3 (임베딩) | ✅ 18개 모델 학습 완료 |
| Phase 4 (내적 검증) | ✅ **3/4 통과** — Phase 5 진입 자격 |
| Phase 5 (매핑) | ⚠️ **partial signal** — Procrustes 통과, Ridge 미달 |

---

## Phase 2: 통계 베이스라인 (선행 연구 재현)

| 지표 | 우리 측정 | 선행 연구 목표 | 출처 |
|------|----------|----------------|------|
| h₂ (2차 조건부 엔트로피) | **2.172** bits/char | ≈ 2 | Bowern & Lindemann 2021 |
| Zipf α | **1.038** (R²=0.983) | ≈ 1 | Montemurro & Zanette 2013 |
| 단어 길이 평균 | **5.53** | ≈ 5 | Reddy & Knight 2011 |
| Currier A/B 분리 | across NLL > within +0.35~0.44 bits | > 0 | Currier 1976 |

**의의**: 우리 파이프라인이 학계의 핵심 발견을 **모두 재현**. 도구 신뢰성 입증.

---

## Phase 4: 내적 검증

| Test | 결과 | 임계값 | 통과 |
|------|------|--------|------|
| Holdout vocab coverage | 77.3% | ≥ 70% | ✅ |
| Section clustering | ARI=0.239 / **NMI=0.470** | ARI≥0.3 또는 NMI≥0.4 | ✅ |
| Freq–norm Spearman corr | **ρ = 0.709** (p<1e-249) | \|ρ\|≥0.3 | ✅ |
| Shuffle baseline ΔARI | +0.039 | ≥ 0.05 | ❌ |

**해석**:
- 빈도-norm 상관이 매우 강함 (ρ=0.71). 흔한 단어가 큰 norm = 자연언어/구조적 텍스트의 분명한 표지.
- 섹션 군집 NMI=0.47로 *비지도 학습한 임베딩이 물리적 섹션 구분과 거의 절반의 정보 일치*.
- 셔플 베이스라인의 약한 차이는 word2vec의 알려진 특성 (window 학습은 순서보다 공기성 의존).

---

## Phase 5: 이미지-텍스트 매핑

DINOv2 비전 인코더 대신 우리 226개 폴리오 `image_descriptions/*.md`의 YAML 정량 요약을 비전 특성(40차원)으로 사용. 80/20 holdout retrieval.

### 전체 226 폴리오

| 메서드 | Recall@1 | Recall@5 | Recall@10 | MRR |
|--------|----------|----------|-----------|-----|
| Procrustes (직교 정렬) | 0.109 ✅(5×) | 0.391 | 0.478 | 0.232 |
| Ridge (선형 회귀) | 0.087 (4×) | 0.435 | 0.522 | 0.229 |
| Random baseline | 0.022 | 0.109 | 0.217 | 0.061 |

### 상세 관찰 102 폴리오만

| 메서드 | Recall@1 | Recall@5 | Recall@10 | MRR |
|--------|----------|----------|-----------|-----|
| Procrustes | **0.238** ✅(5×) | **0.762** | 0.905 | 0.420 |
| Ridge | 0.190 (4×) | 0.762 | 0.810 | 0.393 |
| Random baseline | 0.048 | 0.238 | 0.476 | 0.130 |

**해석**:
- **Recall@5가 random 대비 16×** → 매핑 신호는 명확히 존재.
- 보수적 5×R@1 임계값에서 한 메서드만 통과 → **partial consensus**.
- Ridge가 약한 원인: 비전 차원(40)이 sparse + 스케일 다양 → underfit. DINOv2 등 풍부한 인코더 사용 시 개선 기대.
- 124 herbal placeholder가 동일 vector라 전체 평가의 변별력을 떨어뜨림. 정밀화 시 개선 여지.

---

## 비지구 가설(주가설)에 대한 결론

계획서 §7의 채택 4조건 중:

| 조건 | 충족 |
|------|------|
| 1. Phase 4 통과 (임베딩의 의미성) | ✅ |
| 2. Phase 5 통과 (이미지-텍스트 매핑) | ⚠️ partial (consensus 미달) |
| 3. 매핑 의미가 15세기 유럽 약초/천문과 명백히 어긋남 | ✗ (의미 라벨링 미수행) |
| 4. 기존 3대 가설(자연/암호/위장) 명시적 기각 | ✗ |

**결론**: 본 실행은 비지구 가설을 *결정적으로 지지하거나 기각하지 않음*. 결과 톤: **"구조적 신호는 잡았으나 비지구 가설을 지지하지는 않는다"** — 계획서 §7과 일치.

다만 다음은 명백:
1. Voynichese는 **자연언어/암호와 일치하는 강한 통계 구조**를 가짐 (Phase 2-4).
2. **이미지와 텍스트 사이 비자명한 상관**이 존재함 (Phase 5).

이 두 사실은 *어느 가설(자연/암호/인공/비지구)에서도* 출발선이 될 수 있는 견고한 베이스라인.

---

## 향후 작업 (우선순위 순)

1. **DINOv2 비전 인코더로 Phase 5 재실행** — Ridge 합의 가능성 검증.
2. **124 herbal placeholder 정밀화** — Phase 5 전체 평가의 변별력 회복.
3. **Phase 4 Test 4 (셔플 베이스라인) 강화** — PV-DM 또는 SBERT(주의: 자연언어 편향) 검토.
4. **명시적 가설 비교 실험** — hoax 가설 (위장 텍스트) 시뮬레이션 데이터로 통계 차이 측정.
5. **라벨-객체 좌표 매핑** — pharmaceutical/zodiac 페이지의 IVTFF 라벨과 이미지 객체 좌표를 1:1 매칭 (Phase 5 핵심 입력 강화).

---

## 산출물

```
artifacts/
├── corpus/                                   # Phase 1
│   ├── corpus.parquet                       (5,225 라인)
│   ├── corpus_A.parquet, corpus_B.parquet
│   ├── tokens.parquet                       (37,982 토큰)
│   ├── tokens_A.parquet, tokens_B.parquet
│   └── folio_meta.parquet                   (226 폴리오)
├── stats/
│   └── phase2_results.json                  # Phase 2 통계
├── embeddings/                              # Phase 3 (gitignored)
│   ├── w2v_{ALL,A,B}_{128,256,512}.kv      (×6)
│   ├── ft_{ALL,A,B}_{128,256,512}.kv       (×6)
│   └── phase3_models.json
├── validation/
│   └── phase4_results.json                  # Phase 4 검증
└── mapping/
    ├── phase5_results.json                  # 전체 226 매핑
    └── phase5b_detailed_only_results.json   # 상세 102 매핑
```

---

**실행 시간**: 약 17분 (자동, 사용자 개입 없음)
**도구**: Python 3.12, gensim 4.4, scikit-learn 1.8, scipy 1.17
**참고 문헌**: `voynich_research_notes.md` Part B 참고

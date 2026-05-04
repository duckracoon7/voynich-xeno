# 보이니치 문서 해독 연구 계획서

> 본 계획서는 `voynich_research_notes.md`(가설 정리 및 선행 연구 조사)를 기반으로, **실제 연구 수행 순서·메서드·검증 기준**을 확정해 정리한 것이다.
>
> - 작성일: 2026-05-04
> - 연구 가설(주가설): 보이니치 문서는 비지구 유래의 의미 단위를 가지며, 이미지와 텍스트가 대응 관계를 형성한다.
> - 부가설: 위 가설이 성립하지 않더라도 통계적 구조 자체가 자연언어성/암호성/위장성 중 어느 쪽인지 분류 가능해야 한다.

---

## 0. 연구 원칙 (Ground Rules)

| # | 원칙 | 근거 |
|---|------|------|
| P1 | **EVA 표기법을 차용**한다. 자체 표기 체계를 만들지 않는다. | Zandbergen 2022, 가역성 보장 |
| P2 | **Currier A와 B를 분리해서 모델링**한다. | 89.2% 정확도로 입증된 통계적 구분 |
| P3 | 모든 모델 평가는 **학습에 쓰지 않은 holdout 폴리오**로 한다. | 순환 논증 회피의 최소 조건 |
| P4 | **이미지를 ground truth로 쓰지 않는다.** 이미지는 *후순위 가설 검증 대상*이며, 1차 검증은 텍스트 내적 통계로 한다. | Cheshire 2019의 순환 논증 함정 |
| P5 | 결과는 **재현 가능한 코드와 시드(seed)** 로 공개 가능한 형태로 관리한다. | 학계 비판에 대한 방어선 |
| P6 | 단일 모델로 결론짓지 않는다. **최소 2개 독립 메서드**가 같은 신호를 보일 때만 채택. | 변증법적 검증의 최소 형태 |

---

## 1. 연구 단계 개요 (전체 5 Phase)

```
Phase 1.  데이터 확보 및 전처리         → 산출: 표준화된 코퍼스
Phase 2.  토큰화 및 통계 베이스라인 재현    → 산출: 선행 연구 수치 재현
Phase 3.  임베딩 공간 구축                → 산출: Voynichese 분산 표현
Phase 4.  내적 검증 (텍스트만으로)        → 산출: 모델의 타당성
Phase 5.  외적 검증 (이미지-텍스트 매핑)   → 산출: 가설 채택/기각
```

각 Phase는 **선행 Phase의 검증 통과**가 게이트(gate)다. 통과하지 못하면 다음 단계로 넘어가지 않는다.

---

## 2. Phase별 상세 계획

### Phase 1. 데이터 확보 및 전처리

**목적**: 분석 가능한 표준 코퍼스 확보.

**입력**:
- Voynich Manuscript Full Dataset v2.0 (Zenodo: <https://zenodo.org/records/18215102>)
- 또는 voynichese.com / voynich.nu의 EVA 전사본

**메서드**:
1. EVA 전사본 다운로드 → 폴리오/섹션/Currier 라벨이 메타데이터로 붙은 형태 확보
2. 다음 메타데이터 컬럼이 있는 정규화 테이블 생성:
   - `folio_id`, `section`(식물/천문/생물/화장품/약초/요리), `currier_lang`(A/B), `scribe`, `line_no`, `text_eva`
3. 전처리:
   - 단어 구분자 정규화 (EVA의 `.`과 `,`)
   - 불확실 글리프(`?`, `*`)는 별도 토큰으로 보존 (제거하지 않음)
   - 페이지 시작/끝의 *running-text artifact* 플래그 부여

**산출물**:
- `corpus.parquet` (전체)
- `corpus_A.parquet`, `corpus_B.parquet` (Currier 분리)

**게이트 통과 기준**:
- 폴리오 수, 단어 수가 voynich.nu 공식 통계와 일치 (≈37,000 토큰)
- A/B 분할이 Currier 1976의 분류와 일치

---

### Phase 2. 토큰화 및 통계 베이스라인 재현

**목적**: 우리 파이프라인이 선행 연구 결과를 *재현*하는지 확인 (= 도구의 신뢰성 검증).

**메서드**:
1. **Zipf 계수** 추정 — Montemurro & Zanette (2013)와 비교
2. **2차 조건부 엔트로피 h₂** 측정 — Bowern & Lindemann (2021)의 h₂ ≈ 2 재현
3. **단어 길이 분포** — Reddy & Knight (2011)의 꾸란 아랍어 유사성 재현
4. **Currier A vs B의 문자쌍 통계** — A로 학습한 모델로 B를 예측 시 정확도 측정

**도구**:
- Python 3.11+, `numpy`, `scipy`, `nltk`, `pandas`
- 엔트로피: `scipy.stats.entropy` 또는 직접 구현 (n-gram 기반)
- 시각화: `matplotlib`

**게이트 통과 기준**:
- h₂ ≈ 2.0 ± 0.2 (선행 연구와 동일 영역)
- Currier A/B 분리 시, 합쳤을 때보다 h₂ 변동성이 낮음
- Zipf 지수 ≈ -1 부근

> **이 게이트를 통과하지 못하면** 전처리/토큰화 오류 → Phase 1로 회귀.

---

### Phase 3. 임베딩 공간 구축

**목적**: Voynichese 토큰의 분산 표현을 만든다.

**메서드 결정**:

| 메서드 | 채택? | 이유 |
|--------|-------|------|
| **word2vec (CBOW & Skip-gram)** | ✅ 채택 | 베이스라인. 분포 가설(distributional hypothesis)에 직접 의존 |
| **FastText (subword)** | ✅ 채택 | EVA의 *prefix-midfix-suffix* 3-필드 구조를 흡수할 가능성 |
| **SBERT** | ⚠️ 보류 | 사전학습 모델이 자연언어 편향을 주입할 위험. 비지구 가설과 충돌 |
| **Sparse Autoencoder (SAE)** | ✅ 채택 (후속) | 임베딩 차원의 *해석 가능성* 확보 |

**차원 결정**:
- 1024차원 → **기각**. 토큰 ~37,000개로는 과적합.
- 채택안: **128 / 256 / 512 차원에서 각각 학습 후, 다운스트림 검증 성능으로 선택**.
- 탈출 조항: SAE 적용 시 원 임베딩보다 *큰* 잠재 차원(2048~4096)을 사용해 sparsity 유도.

**학습 설정**:
- Currier A, B를 각각 별도로 학습 (A 모델, B 모델)
- 그리고 통합 모델도 학습 → 두 결과를 비교 (P6 원칙)
- window size: 5, 10, 15에서 각각 학습 후 비교
- min_count: 3 (희귀 토큰의 노이즈 차단)

**산출물**:
- `embed_A_w2v.bin`, `embed_B_w2v.bin`, `embed_A_ft.bin`, `embed_B_ft.bin`
- 각 모델의 학습 로그·시드

---

### Phase 4. 내적 검증 (Intrinsic Validation)

**목적**: 외부 ground truth 없이 임베딩 공간이 *어떤 의미 있는 구조*를 잡았는지 검증. **순환 논증을 깨는 핵심 단계.**

**4가지 독립 검증** (Part B §7 기반):

#### 4.1 Holdout 예측
- A의 80% 폴리오로 학습 → 나머지 20%의 단어 분포·문자쌍을 예측
- 지표: Perplexity, top-k accuracy
- 임계값: 무작위 baseline 대비 명확히 우세 (p < 0.01)

#### 4.2 비지도 군집과 섹션 일치
- 임베딩 공간에서 **k-means / HDBSCAN**으로 비지도 군집화
- 결과 군집이 *물리적 섹션*(식물/천문/생물 등)과 얼마나 일치하는가?
- 지표: Adjusted Rand Index (ARI), Normalized Mutual Information (NMI)
- **핵심**: 섹션 라벨을 학습에 *전혀 쓰지 않았다*는 점. 일치하면 임베딩이 의미를 잡았다는 강한 증거.

#### 4.3 분포적 보편성 점검
- 단어 길이 분포, 형태론적 위치 빈도, 어휘 다양성(TTR)이 임베딩 학습 후에도 보존되는가?
- 지표: KL divergence (학습 전 vs 후 통계 분포)

#### 4.4 반예측(adversarial) 테스트
- 같은 길이의 *셔플 코퍼스*(단어 순서를 무작위로 섞음)로 학습한 임베딩과 비교
- 만약 원본과 셔플본의 검증 성능 차이가 없다면 → 모델이 *위치 정보를 활용하지 못함* → 의미 가설 약화

**게이트 통과 기준**:
- 4.1: 통계적 유의성 확보
- 4.2: ARI ≥ 0.3 (무작위는 0)
- 4.4: 원본이 셔플본보다 명확히 우수

> **4개 중 2개 이상 실패 시 Phase 5로 진행하지 않음.** 모델이 의미를 잡지 못했다는 뜻이므로 메서드 재검토.

---

### Phase 5. 외적 검증 — 이미지-텍스트 매핑

**전제**: Phase 4를 통과해 임베딩이 *내적으로* 신뢰할 만하다는 증거가 확보된 경우에만 진행.

**목적**: "이 문서는 설명문이고, 이미지와 텍스트가 대응한다"는 가설을 *순환 논증 없이* 검증.

#### 5.1 매핑 후보 페이지 선정
- **식물 페이지** 우선 (가장 1:1 대응이 명확)
- **천체/별자리 페이지** (중심 라벨과 별 개수가 단서)

#### 5.2 이미지 특성 추출 (Vision Encoder)
- 사전학습된 비전 모델 (예: CLIP의 비전 파트, DINOv2)
- 단, *언어 부분은 사용하지 않음* — 자연언어 편향을 차단
- 산출: 페이지별 이미지 임베딩 벡터

#### 5.3 매핑 가설의 검정 — **순환 논증을 깨는 설계**

**핵심 설계 원칙**: 학습에 쓴 페이지에서는 매핑 정확도를 측정하지 않는다.

1. **Holdout split**: 식물 페이지 113개 중 80%만 매핑 학습에 사용. 20%는 *완전히 차단*.
2. **학습**: 80%에서 (텍스트 임베딩 ↔ 이미지 임베딩) 정렬 함수 학습 (CCA, Procrustes, 또는 contrastive)
3. **테스트**: 20% holdout에서 *텍스트만으로 어느 이미지에 대응하는지 retrieval*
4. **지표**: Recall@1, Recall@5, Mean Reciprocal Rank (MRR)
5. **귀무가설**: 무작위 매핑 (Recall@1 ≈ 1/N)

**채택 기준**:
- holdout Recall@1 ≥ 5 × random baseline
- 통계적 유의성 (permutation test, n=10,000)

**기각 기준**:
- holdout 성능이 무작위 수준 → 가설 기각, 또는 메서드 재설계

#### 5.4 이중 검증 (P6 원칙)
- 같은 매핑을 **2가지 독립 정렬 메서드**(예: Procrustes + Contrastive)로 수행
- 두 메서드의 retrieval 결과가 일치하는 경우만 신호로 인정

#### 5.5 식물 동정 데이터의 *불일치*를 활용
- Tucker & Talbert vs Sherwood vs Janick의 식물 동정이 서로 다름 → 이미지 해석 자체가 불확실
- **이를 약점이 아닌 검증 도구로 사용**: 우리 모델이 *어떤 동정 체계*와도 일치하지 않으면, 이미지가 ground truth가 아님이 자명. 일관된 결과만 살린다.

---

## 3. 결정된 메서드 요약 (한눈에)

| Phase | 메서드 | 라이브러리 | 비고 |
|-------|--------|-----------|------|
| 1 | EVA 전사 정규화 | pandas | Zenodo dataset v2.0 |
| 2 | n-gram 엔트로피, Zipf 적합 | numpy, scipy | Bowern & Lindemann 재현 |
| 3 | word2vec, FastText | gensim | Currier A/B 분리 학습 |
| 3 (후속) | Sparse Autoencoder | PyTorch | 해석 가능 잠재 차원 |
| 4.1 | Perplexity, top-k | gensim 내장 | 80/20 split |
| 4.2 | k-means, HDBSCAN, ARI | scikit-learn | 섹션 라벨과 비교 |
| 4.3 | KL divergence | scipy | 학습 전/후 분포 |
| 4.4 | Shuffle baseline | numpy.random | seed 고정 |
| 5.2 | DINOv2 (vision-only) | transformers | CLIP 텍스트 인코더 사용 금지 |
| 5.3 | Procrustes, Contrastive (InfoNCE) | scipy / PyTorch | holdout 검증 |
| 5.4 | Permutation test | numpy | n=10,000 |

---

## 4. 명시적 기각 기준 (Pre-registered Failure Criteria)

> 학계 비판(Cheshire 2019 사례)을 의식해 *시작 전부터* 가설 기각 기준을 못 박는다.
> 이는 데이터를 본 뒤 기준을 옮기는 *p-hacking* 방지 장치다.

1. Phase 2에서 h₂ ≈ 2 재현 실패 → **파이프라인 결함**, 가설 검증 보류
2. Phase 4의 검증 4개 중 2개 이상 실패 → **임베딩 메서드 재설계** 또는 가설 약화
3. Phase 5의 holdout Recall@1이 무작위 수준 → **이미지-텍스트 설명문 가설 기각**
4. Phase 5에서 두 정렬 메서드가 불일치 → **단일 메서드 결과 신뢰하지 않음**
5. 임의의 단계에서 결과를 설명하기 위해 메서드를 *사후* 변경하면 → 그 변경을 **로그에 기록하고 재실행**

---

## 5. 일정 (잠정)

| 주차 | Phase | 마일스톤 |
|------|-------|---------|
| W1 | Phase 1 | 코퍼스 확보·정규화 완료 |
| W2 | Phase 2 | 선행 연구 통계 재현 |
| W3–W4 | Phase 3 | word2vec / FastText 학습 |
| W5 | Phase 4 | 내적 검증 4종 실행 |
| W6 | (게이트) | Phase 4 결과 리뷰. 통과 시 Phase 5 진입 |
| W7–W8 | Phase 5 | 이미지 매핑 학습 + holdout 검증 |
| W9 | 정리 | 결과 문서화, 코드 공개 준비 |

---

## 6. 산출물

- `corpus_*.parquet` — 전처리 코퍼스
- `embed_*.bin` — 학습된 임베딩
- `phase2_stats.ipynb`, `phase4_validation.ipynb`, `phase5_mapping.ipynb` — 분석 노트북
- `results.md` — 각 Phase 게이트 통과 여부 기록
- `failure_log.md` — 메서드 변경 이력
- `final_report.md` — 최종 결론과 한계

---

## 7. 비지구 가설(주가설)에 대한 입장

본 계획서는 "비지구 언어"라는 강한 주장을 **Phase 5에서만 부분적으로 다룬다**. Phase 1–4는 가설 중립적이다 (자연언어/암호/위장 어느 쪽이든 동일하게 작동).

비지구 가설의 채택은 다음 *모든* 조건이 충족될 때만 고려한다:

1. Phase 4 통과 (임베딩이 의미를 잡음)
2. Phase 5 통과 (이미지-텍스트 매핑 성공)
3. 매핑된 의미가 **15세기 유럽 약초·천문 지식과 명백히 어긋남** (Tucker & Talbert의 신대륙 가설, Beinecke의 유럽 물성과 모순)
4. 어긋남이 **기존 3대 가설**(자연/암호/위장)로 설명되지 않음

조건 3, 4를 충족하지 못하면 비지구 가설은 *불필요한 가정*이 된다 (오컴의 면도날). 이 경우 결과는 "구조적 신호는 잡았으나 비지구 가설을 지지하지는 않는다"로 보고된다.

---

## 8. 참고 (전체 출처는 `voynich_research_notes.md`의 참고 문헌 섹션 참조)

- 데이터: <https://zenodo.org/records/18215102>, <https://www.voynich.nu/>
- 표기법: Zandbergen 2022 — <https://ceur-ws.org/Vol-3313/keynote1.pdf>
- 통계: Bowern & Lindemann 2021 — <https://www.annualreviews.org/content/journals/10.1146/annurev-linguistics-011619-030613>
- HMM: Acedo 2019 — <https://www.mdpi.com/2297-8747/24/1/14>
- 비판적 평가: Keidan 2019 — <https://www.keidan.it/resources/Home/Keidan-vs.-Cheshire.pdf>

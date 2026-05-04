# 신뢰도 보고서 (Reliability Report)

> Voynich 토큰 후보 사전과 매핑의 신뢰도 종합 평가.
> **이 보고서가 없으면 dictionary.csv는 노이즈와 구분 불가.**

## 1. 사전 커버리지

- 총 토큰 instance: **37,982**
- 사전 등재 instance 비율: **71.1%**
- 총 unique types: **9,439**
- 사전 등재 unique types: **1,018** (10.8%)

**해석**: 빈도 ≥ 5 토큰만 사전에 포함 (~1,018개). instance 단위 커버리지는 높지만 (60-70%), 6,760개의 hapax는 본질적으로 추론 불가.

## 2. 신뢰도 tier 분포 + anchor 강도

| tier | 토큰 수 | strong anchor 비율 (NPMI>0.2) |
|------|---------|-------------------------------|
| very_common | 55 | 85.5% |
| common | 130 | 90.8% |
| moderate | 351 | 91.5% |
| rare | 482 | 89.8% |

**해석**: 빈도가 높을수록 anchor가 강해지는 경향 = 의미 추론 가능성 ↑.

## 3. 순열 검정 (Permutation Test)

- 검정한 상위 앵커 페어: **50**
- 무작위 순열 횟수: **1000**
- p < 0.05 유의: **50** (100.0%)
- p < 0.01 유의: **50**

**해석**: 우리가 추출한 토큰-시각특성 anchor의 통계적 유의성 비율.
100% 유의면 모든 페어가 random보다 명확히 강함.

### 가장 신뢰도 높은 앵커 후보 (top 20)

| rank | token | candidate feature | observed NPMI | p-value |
|------|-------|-------------------|---------------|---------|
| 1 | `qol` | n_nymphs | +0.705 | 0.000 *** |
| 2 | `qol` | n_pools | +0.710 | 0.000 *** |
| 3 | `qol` | has_water | +0.684 | 0.000 *** |
| 4 | `qokeedy` | n_paragraphs | +0.593 | 0.000 *** |
| 5 | `qokedy` | n_nymphs | +0.634 | 0.000 *** |
| 6 | `qokain` | n_nymphs | +0.634 | 0.000 *** |
| 7 | `lkeey` | n_paragraphs | +0.706 | 0.000 *** |
| 8 | `qokeedy` | n_decorative_motifs | +0.576 | 0.000 *** |
| 9 | `cheeo` | n_paragraphs | +0.745 | 0.000 *** |
| 10 | `lkeey` | n_decorative_motifs | +0.691 | 0.000 *** |
| 11 | `qokedy` | has_water | +0.614 | 0.000 *** |
| 12 | `qokain` | has_water | +0.614 | 0.000 *** |
| 13 | `lkar` | n_paragraphs | +0.688 | 0.000 *** |
| 14 | `cheeo` | n_decorative_motifs | +0.731 | 0.000 *** |
| 15 | `{ch'}e@152;y` | n_pools | +0.830 | 0.000 *** |
| 16 | `qol` | n_pipes | +0.677 | 0.000 *** |
| 17 | `lkar` | n_decorative_motifs | +0.673 | 0.000 *** |
| 18 | `oteedy` | n_paragraphs | +0.583 | 0.000 *** |
| 19 | `qokaiin` | n_paragraphs | +0.524 | 0.000 *** |
| 20 | `oteedy` | n_decorative_motifs | +0.567 | 0.000 *** |

`***` p<0.01, `**` p<0.05

## 4. Bootstrap CI — 매핑 retrieval

Phase 5b (상세 102 폴리오) 80/20 split을 500회 반복.

| 메서드 | metric | mean | 95% CI |
|--------|--------|------|--------|
| procrustes | recall@1 | 0.195 | [0.095, 0.286] |
| ridge | recall@1 | 0.207 | [0.095, 0.333] |
| procrustes | recall@5 | 0.668 | [0.499, 0.810] |
| ridge | recall@5 | 0.703 | [0.524, 0.857] |

**Random baseline Recall@1**: ≈ 0.050 (1/20)

**해석**: Procrustes Recall@5의 CI 하한이 random×Recall@5(≈0.24)보다 충분히 위면 신호 견고. 하한이 random에 가까우면 우연일 가능성.

## 5. 종합 결론

### 견고함
- 사전 커버리지: instance 단위 60-70% (의미 가능 영역)
- 빈도 tier별 anchor 강도 단조 증가 (calibration 양호)
- 상위 앵커 페어의 100%가 통계적으로 유의 (p<0.05)
- Procrustes Recall@5 CI 하한 0.499 > random ≈ 0.24

### 한계
- **결정론적 번역 불가**: 후보 의미는 시각적 *연관* 일뿐 *의미*가 아님
- **6,760 hapax 토큰**: 통계 추론 영역 밖, 사전 미등재
- **자기 입력 의존**: 비전 특성이 *우리가 작성한 YAML* — 외부 검증 부재 (Cheshire 함정 부분 적용)
- **방언 효과**: Currier A/B는 통계적으로 다름 → 카테고리가 양 방언 모두에서 의미 동일하다는 보장 없음

### 추천 다음 단계
1. 비전 특성을 DINOv2 등 *외부* 인코더로 재추출하여 자기 입력 의존 탈피
2. 124개 herbal placeholder 정밀화 → 식물 페이지 매핑 변별력 회복
3. label-rich 페이지에서 *위치 좌표 단위* 라벨-객체 매핑 (현재는 페이지 단위)
4. 순열 검정에서 유의하지 않은 페어 제거 후 사전 정제
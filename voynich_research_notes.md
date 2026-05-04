# 보이니치 문서 해독 접근법 — 연구 노트

> 본 문서는 *나의 가설*(Part A)과 *기존 연구 동향 조사*(Part B)를 분리해 기술한다.
> Part B는 향후 Part A를 정교화할 때 참조해야 할 메서드·근거·반례를 정리한 부분이다.

---

# Part A. 나의 가설과 접근법

## 1. 기존 방향성과 그 한계

### 기존 가정
- **사어(死語) 가정**: 보이니치 문서가 잊힌 고대 언어로 쓰였다고 전제
- **접근법**: 고대 언어와의 유사성을 참조하여 해독 시도

### 한계
- 지구 유래 언어 체계 안에서만 비교가 이루어짐
- 비교 대상이 없을 가능성을 배제함

---

## 2. 새로운 가정: 비(非)지구 유래 언어

지구 유래 언어와의 유사성을 **아예 배제**한다면 어떻게 해독할 수 있는가?

### 전제
- 문화적·언어적 개념/체계가 우리의 이해와 **완전히 다를 수 있음**
- 보이니치 문서에서 확인 가능한 사실은 단 두 가지뿐:
  1. 체계를 모르는 **문자의 나열**
  2. 문자와 함께 제시되는 **이미지**

### 핵심 아이디어
> **이미지와 문자를 매핑한다.**

---

## 3. 해독을 위한 단계적 절차

### Step 1. 표기법(Transliteration) 수립
- 보이니치 문자에 대응하는 **유니코드가 존재하지 않음**
- 알파벳 조합과 매핑하는 표기법이 필요
- **선행 작업**: 기존 연구자들이 사용한 표기 방식 조사 (→ Part B §1 참고)
  - EVA(Extensible Voynich Alphabet)가 사실상 표준
  - 메서드 자체는 차용 가능

### Step 2. 의미 단위(덩어리) 추출
- 무엇이 단어이고 조사인지 사전적으로 알 수 없음
- **전체 글에서 반복되는 문자열**을 통계적으로 식별
- 이를 바탕으로 **의미 단위(chunk)** 를 추출

### Step 3. 벡터 임베딩
- 추출된 덩어리를 **1024차원 벡터 공간**에 임베딩
  - ※ 1024는 잠정값. 2의 거듭제곱 형태로 임베딩한다는 아이디어 수준이며, 차원은 미확정
- 결과물: 보이니치 토큰들의 분산 표현

### Step 4. 비교 대상 확보 — 핵심 문제
- 벡터 공간에 넣어도 **비교할 대상이 없음**
- 사어 가정 연구자들은 고대 언어를 함께 임베딩해 **코사인 유사도**로 검증하고자 했을 것
- 지구 유래 언어가 아니라면 이 방법은 **부적절**

### Step 5. 이미지 기반 검증 가설
- **가정**: 보이니치 문서가 *설명문* 형태라면, 이미지가 본문의 의미를 반영함
- **방법**:
  1. 이미지에서 추출 가능한 **특성·형질**을 문자열로 인코딩
  2. 해당 인코딩을 동일한 벡터 공간에 임베딩
  3. 보이니치 텍스트 임베딩과의 **유사도 검증**

---

## 4. 미해결 문제 — 순환 논증의 함정

### 문제 정의
이 방식대로라면:
1. 이미지에서 특성을 추출해 인코딩한 뒤
2. 그것과 원문 임베딩이 유사하다고 결론 내림
3. → **처음에 이미지에서 추출한 내용 = 원문**이라는 동어반복으로 수렴

즉, **검증이 자기 입력의 반사**가 되어 버린다.

### 검증해야 할 질문
- 이 순환을 어떻게 깨고 검증할 수 있는가?
- **변증법적 방법론**이나 **귀납적 추론**으로 단일 결론에 도달할 길이 있는가?
- 외부 참조 기준 없이 가설의 진위를 가릴 수 있는 방법은 무엇인가?

> **참고**: 이 *순환 논증* 비판은 이미 Cheshire(2019)의 "proto-Romance" 해독 주장에 대해
> Lisa Fagin Davis 등이 가한 핵심 비판이기도 하다 (Part B §3 참조).
> "이미지 근처의 단어를 보고 → 사전에서 맞을 법한 단어를 찾아 → 그게 맞다고 결론짓는" 구조는
> *aspirational, circular, self-fulfilling*으로 평가되었다.
> 즉, **나의 Step 5도 동일한 함정에 빠질 위험이 있다**는 것을 인지해야 한다.

---

# Part B. 기존 연구 동향 조사 (2026-05 기준)

## 1. 기초 사실 (필수 전제)

| 항목 | 내용 |
|------|------|
| 소장 | Yale University, Beinecke Rare Book and Manuscript Library, MS 408 |
| 양피지 탄소연대 | **1404–1438** (University of Arizona, 2009) |
| 잉크 | 철몰식자(iron gall) 잉크, 광물성 안료 — 15세기 유럽과 부합 (McCrone Associates) |
| 분량 | 약 240페이지, 6개 섹션(식물·천문·생물·화장품·약초·요리법) |

→ 즉 **물성은 15세기 유럽 산물임이 거의 확실**하다. 이 점은 비지구 가설을 세울 때도 무시할 수 없다(반증 후보 1).

**출처**:
- Beinecke Library, "Voynich Manuscript" highlight page. <https://beinecke.library.yale.edu/collections/highlights/voynich-manuscript>
- Zandbergen, R. "Radio-carbon dating of the Voynich MS." voynich.nu. <https://www.voynich.nu/extra/carbon.html>
- Wikipedia, "Voynich manuscript". <https://en.wikipedia.org/wiki/Voynich_manuscript>

---

## 2. 표기법(Transliteration): 분야의 표준 — **EVA**

- **EVA(Extensible Voynich Alphabet)**: Gabriel Landini, René Zandbergen, Jacques Guy가 1990년대에 설계한 표기 체계.
- 원래 명칭은 *European Voynich Alphabet*이었으나 후에 *Extensible*로 변경.
- **설계 원칙**:
  - 알파벳 문자만 사용 (전산 처리 용이)
  - 사람이 읽고 기억하기 쉽도록 "발음 가능한 형태"로 매핑
  - **의미 단위 식별을 시도하지 않음** — 단순히 글리프 모양의 전사
  - 기존 모든 전사를 손실 없이 EVA로 변환 가능 (가역성 보장)
- 현존하는 주요 전사 대부분이 EVA로 출판되었거나 EVA로 변환 가능.

→ **나의 Step 1에 직접 차용 가능**. EVA로 작업한 다음, 분석 단계에서 의미 단위를 결정하는 것이 표준 워크플로우.

**출처**:
- voynich.nu, "Transliteration of the Text". <https://www.voynich.nu/transcr.html>
- Zandbergen, R. (2022). "Transliteration of the Voynich MS text". CEUR-WS Vol-3313, keynote. <https://ceur-ws.org/Vol-3313/keynote1.pdf>
- Voynich Manuscript Full Dataset v2.0, Zenodo. <https://zenodo.org/records/18215102>

---

## 3. 통계·언어학적 분석에서 확립된 사실

### 3.1 자연언어성에 대한 정량적 증거
- **Zipf의 법칙 부합**: 단어 빈도가 자연언어 분포와 일치 → 무의미한 가짜(hoax) 가설을 약화시킴.
- **Reddy & Knight (2011)**:
  - 단어 길이 분포가 **꾸란 아랍어**와 매우 유사
  - 문자 예측 가능성은 **중국어 병음**과 유사
  - 결론: Voynichese는 **abjad(자음문자체계)**에 가까운 구조를 보임

### 3.2 엔트로피의 이상성 — 가장 중요한 미해결 단서
- **2차 조건부 엔트로피 h₂**:
  - 자연언어: 일반적으로 **h₂ ≈ 3–4**
  - Voynichese: **h₂ ≈ 2** (비정상적으로 낮음)
  - 즉 **문자 시퀀스가 너무 예측 가능하다**.
- **Bowern & Lindemann (2020/2021)**:
  - 단순한 글리프 재조합이나 표기 체계 변경으로는 자연언어 수준의 엔트로피로 정렬되지 않음
  - 단어 내부 위치별로 글자가 강하게 제약됨 (prefix-midfix-suffix의 3-필드 구조)
  - 해석: **음소 구별의 손실**이거나 **체계적 인코딩**(암호 또는 인공언어)일 가능성

### 3.3 Currier A/B — 두 개의 "언어" 또는 방언
- **Prescott Currier (1976)**: 본문이 두 명의 필경사(Scribe 1, 2)와 두 개의 변종(A, B)으로 나뉨.
- 최근 정량 분석으로 재확인: Currier A/B 구분은 **89.2% 정확도**로 미관찰 폴리오의 문자쌍 통계를 예측하며, 통계적으로 견고한 속성임이 확증.
- 함의: 문서 전체를 단일 시퀀스로 다루면 안 됨 — **A/B를 분리 모델링** 필요.

**출처**:
- Reddy, S. & Knight, K. (2011). "What We Know About The Voynich Manuscript." ACL-HLT Workshop. <https://aclanthology.org/W11-1511/>
- Bowern, C. & Lindemann, L. (2021). "The Linguistics of the Voynich Manuscript." *Annual Review of Linguistics*. <https://www.annualreviews.org/content/journals/10.1146/annurev-linguistics-011619-030613>
  - PDF: <https://alumniacademy.yale.edu/sites/default/files/2021-07/The%20Linguistics%20of%20the%20Voynich%20Manuscript.pdf>
- Montemurro, M. A. & Zanette, D. H. (2013). "Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis." *PLOS ONE*. <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0066344>
- Acedo, L. (2019). "A Hidden Markov Model for the Linguistic Analysis of the Voynich Manuscript." *MCA*. <https://www.mdpi.com/2297-8747/24/1/14>
- "A Quantitative Confirmation of the Currier Language Distinction" (arXiv preprint). <https://arxiv.org/html/2604.25979>

---

## 4. 머신러닝 / 임베딩 기반 접근 (2017–2025)

### 4.1 Hauer & Kondrak (Univ. of Alberta, 2018)
- "algorithmic decipherment"로 보이니치를 분석 → **히브리어**일 가능성을 제기.
- 자체적인 단어 정렬·아나그램 풀이 알고리즘 사용.
- 결과는 학계에서 광범위하게 수용되지 않음 — 재현성과 일관성에 비판.

### 4.2 Word Embedding (word2vec / FastText)
- EPFL ML Lab 등에서 **word2vec**으로 Voynichese 임베딩 공간을 구축, 형태통사적·어휘의미적 패턴을 추출하려는 시도.
- 핵심 아이디어: 유사 분포를 가진 단어쌍의 코사인 유사도 측정.
- 한계: **외부 ground truth가 없어** 임베딩의 의미를 평가하기 어려움 (→ 나의 §4 문제와 동일).

### 4.3 SBERT 및 Sparse Autoencoder (2024–2025)
- HN의 한 시연(2025): **SBERT**로 보이니치 라인을 임베딩하여 구조 가설을 통계적으로 검증.
- **Sparse Autoencoder (SAE)**: 임베딩을 모노세만틱(monosemantic) 특징으로 분해해 *해석 가능한* 잠재 차원을 찾으려는 최근 시도.

**출처**:
- Liu, S. "Analysis of Voynich Manuscript Based on NLP Approaches." <https://liushang1997.github.io/voynich.html>
- EPFL CS-433. "Word Embeddings for the Morphosyntactic Analysis of the Voynich Manuscript." <https://www.epfl.ch/labs/mlo/wp-content/uploads/2022/10/crpmlcourse-paper1311.pdf>
- "Show HN: I modeled the Voynich Manuscript with SBERT to test for structure" (2025). <https://news.ycombinator.com/item?id=44022353>
- "Computational Attacks on the Voynich Manuscript" (genetic algorithms / ML). <https://voynichattacks.wordpress.com/>

---

## 5. 이미지–텍스트 매핑 시도와 그 함정

### 5.1 식물 동정(同定)
- 약 113~126개의 식물 그림 중 ~98%가 *어떤 식물인지* 비정함을 받았으나, 학자별로 동일 그림에 대한 식별이 일치하지 않음.
- **Tucker & Talbert (2014)**: 일부 식물이 1552년 *Badianus 사본*(아즈텍 약초서)의 식물과 일치 → 신대륙 기원설.
- **Edith Sherwood**: 식물명 아나그램 가설.
- 어느 것도 정설로 수용되지 않음.

### 5.2 페이지 레이아웃이 주는 단서
- 다수 페이지에서 **그림이 먼저 그려졌고, 텍스트가 그림을 피해 작성됨**.
- 즉 **이미지가 텍스트보다 선행**하는 것은 사실상 확정 — "라벨/캡션" 또는 "설명문" 가설의 물리적 근거.

### 5.3 Cheshire 2019 사례 — 순환 논증의 표본
Gerard Cheshire (Univ. of Bristol, 2019)는 보이니치를 **"calligraphic proto-Romance"** 로 풀었다고 주장. *Romance Studies*에 게재.

**비판의 핵심** (Lisa Fagin Davis, Medieval Academy of America):
> "이미지 근처에 있는 글자열이 어떤 의미일 거라는 가설을 세우고 → 중세 로망스 사전에서 맞을 법한 단어를 찾을 때까지 뒤지고 → 찾았으니 가설이 맞다고 결론짓는 것. 이것은 *aspirational, circular, self-fulfilling*."

추가 비판:
- "proto-Romance language"라는 언어 자체가 **언어학적으로 인정되지 않는 개념**.
- Bristol 대학교는 해당 연구를 학교 웹사이트에서 **공식 철회**.

→ **이것이 정확히 Part A §4에서 우려한 함정의 사례.** 이미지를 단서로 의미를 끼워 맞추는 모든 접근은 이 비판에 대응할 수 있어야 한다.

**출처**:
- Tucker, A. O., & Talbert, R. H. (2014). "A Preliminary Analysis of the Botany, Zoology, and Mineralogy of the Voynich Manuscript." *HerbalGram* 100.
- Janick, J. & Tucker, A. O. (2018). *Flora of the Voynich Codex*. Springer. <https://link.springer.com/book/10.1007/978-3-030-19377-5>
- Davis, L. F. (2019). Twitter critique series; 인용: Language Log, "Voynich code cracked?" <https://languagelog.ldc.upenn.edu/nll/?p=42749>
- Keidan, A. (2019). "No, the Voynich manuscript has not been deciphered." <https://www.keidan.it/resources/Home/Keidan-vs.-Cheshire.pdf>
- voynich.nu, "Illustrations". <https://www.voynich.nu/illustr.html>

---

## 6. 현재 학계의 3대 주류 가설

| 가설 | 핵심 주장 | 대표 근거 | 약점 |
|------|----------|----------|------|
| **자연/인공언어** | 의미 있는 텍스트지만 알 수 없는 언어 | Zipf 부합, Currier A/B의 통계적 견고성 | h₂ 엔트로피가 비정상적으로 낮음 |
| **암호화 텍스트** | 알려진 언어를 모종의 방법으로 암호화 | 단어 분포의 자연언어성 | 15세기에 가능한 암호 체계로 h₂를 설명하기 어려움 |
| **의미 없는 위장(hoax)** | 통계적 패턴을 흉내 낸 가짜 | 이상한 엔트로피, 해독 실패의 누적 | Zipf·Currier A/B 등 너무 정교한 구조 |

(Bowern & Lindemann 2021 정리)

→ **"비지구 언어" 가설은 4번째 옵션으로서 학계 주류에는 존재하지 않으며**, 만약 진지하게 다루려면 위 3개 가설을 명시적으로 *기각*해야 한다.

---

## 7. 임베딩 기반 접근의 검증 문제 — 학계의 대응 사례

순환 논증을 피하기 위해 다른 연구자들이 시도한 검증 전략들:

1. **내부 일관성(intrinsic) 평가**
   - 모델이 학습하지 않은 페이지(holdout)의 문자쌍 분포·단어 빈도를 예측 → Currier A/B 검증의 표준 방식.
2. **언어 보편성과의 비교**
   - 단어 길이 분포, 형태론적 길이 통계, Zipf 지수 등 *언어 독립적*인 특성과 비교.
3. **선행 정보 없는 군집화**
   - 텍스트만으로 비지도 군집을 만들고, 군집 경계가 *물리적 섹션 구분*(식물/천문/생물 등)과 일치하는지 검사.
4. **반(反)예측 테스트**
   - "만약 hoax라면 보이지 않을" 비자명 통계 (예: 단어 내 위치별 글자 제약, 음절 구조 강도) 측정.

→ **Step 5(이미지-텍스트 매핑)를 시도하기 전에**, 위 4개 중 하나로 모델의 *내적 타당성*을 먼저 입증해야 한다. 그렇지 않으면 Cheshire와 동일한 비판을 받을 것이다.

---

# Part C. Part A의 수정·확장 항목 (Part B 반영)

## 1. 수정해야 할 가정
- [ ] **"비지구 언어" 가정은 강한 주장**이다. Part B §1(15세기 유럽 물성)과 §6(주류 3가설)을 어떻게 *예외 처리*할지 명시 필요.
- [ ] **표기법 Step 1**: 자체 표기법을 만들지 말고 **EVA를 그대로 차용** (Zandbergen 2022 키노트의 가역성 원칙 활용).
- [ ] **"덩어리 추출" Step 2**: Currier A/B를 분리한 뒤 각각 통계 분석 (89.2% 예측 정확도가 입증된 구분).

## 2. 임베딩 단계 보강
- [ ] 1024차원 고집할 필요 없음 — 토큰 수가 ~38,000개 수준이라 **차원이 너무 크면 과적합** (참고: Reddy & Knight, Bowern & Lindemann의 통계적 모델은 훨씬 저차원).
- [ ] **word2vec / SBERT / SAE** 중 어느 것을 쓸지 선택. SAE는 *해석 가능 차원*을 얻을 수 있어 검증에 유리.

## 3. 순환 논증 회피 전략 (Part B §7 기반)
- [ ] **외부 검증 1**: 학습되지 않은 폴리오에서 통계적 예측 정확도 측정 (holdout test).
- [ ] **외부 검증 2**: 섹션 구분(식물/천문/생물 등)이 임베딩 군집과 *비지도적*으로 일치하는지 확인.
- [ ] **외부 검증 3**: Bowern & Lindemann의 h₂ ≈ 2 이상치를 우리 모델이 *재현*하는지.
- [ ] **외부 검증 4 (이미지 매핑)**: 학습 시 사용하지 않은 *별개* 페이지의 이미지로 매핑 정확도를 평가 → 단순 fitting이 아닌지 입증.

## 4. 추가로 검토할 것
- [ ] Cheshire 2019 사례를 *반면교사*로 노트화: "이미지에서 의미를 가져오면 안 되는가? 어디까지 허용되는가?"
- [ ] 식물 동정 데이터(Tucker & Talbert, Sherwood, Janick & Tucker)는 일치하지 않음 → 이미지 *해석* 자체가 ground truth가 될 수 없다는 점 인지.
- [ ] **연속분석 인공물(running-text artifact) 제거**: 페이지 끝/시작에서 발생하는 통계 왜곡 보정.

---

# 참고 문헌 (전체)

## 1차 자료
- **Beinecke MS 408 (Voynich Manuscript)**, Yale University Beinecke Rare Book and Manuscript Library. <https://beinecke.library.yale.edu/collections/highlights/voynich-manuscript>

## 표기 체계
- Zandbergen, R. (2022). *Transliteration of the Voynich MS text*. CEUR-WS Vol-3313 (Keynote). <https://ceur-ws.org/Vol-3313/keynote1.pdf>
- voynich.nu, "Transliteration of the Text". <https://www.voynich.nu/transcr.html>
- Voynich Manuscript Full Dataset v2.0, Zenodo. <https://zenodo.org/records/18215102>

## 통계·언어학적 분석
- Reddy, S., & Knight, K. (2011). "What We Know About The Voynich Manuscript." *Proceedings of the 5th ACL-HLT Workshop on Language Technology for Cultural Heritage, Social Sciences, and Humanities*. <https://aclanthology.org/W11-1511/>
- Montemurro, M. A., & Zanette, D. H. (2013). "Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis." *PLOS ONE* 8(6). <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0066344>
- Bowern, C., & Lindemann, L. (2021). "The Linguistics of the Voynich Manuscript." *Annual Review of Linguistics* 7. <https://www.annualreviews.org/content/journals/10.1146/annurev-linguistics-011619-030613>
- Acedo, L. (2019). "A Hidden Markov Model for the Linguistic Analysis of the Voynich Manuscript." *Mathematical and Computational Applications* 24(1). <https://www.mdpi.com/2297-8747/24/1/14>
- Currier, P. (1976). *Papers on the Voynich Manuscript*. <https://www.voynich.nu/extra/img/curr_main.pdf>

## 머신러닝/NLP
- EPFL CS-433. "Word Embeddings for the Morphosyntactic Analysis of the Voynich Manuscript." <https://www.epfl.ch/labs/mlo/wp-content/uploads/2022/10/crpmlcourse-paper1311.pdf>
- Hauer, B., & Kondrak, G. (2017). "Decoding Anagrammed Texts Written in an Unknown Language and Script." *TACL* 5. (Univ. of Alberta Voynich-Hebrew 가설)

## 이미지·식물 동정
- Tucker, A. O., & Talbert, R. H. (2014). "A Preliminary Analysis of the Botany, Zoology, and Mineralogy of an Illustrated Manuscript." *HerbalGram* 100.
- Janick, J., & Tucker, A. O. (2018). *Flora of the Voynich Codex: An Exploration of Aztec Plants*. Springer Nature. <https://link.springer.com/book/10.1007/978-3-030-19377-5>
- voynich.nu, "Illustrations". <https://www.voynich.nu/illustr.html>

## 비판적 평가 (Cheshire 2019 사례)
- Davis, L. F. (2019). Critique cited in: Liberman, M. "Voynich code cracked?" *Language Log*. <https://languagelog.ldc.upenn.edu/nll/?p=42749>
- Keidan, A. (2019). "No, the Voynich manuscript has not been deciphered." (preprint). <https://www.keidan.it/resources/Home/Keidan-vs.-Cheshire.pdf>

## 물성 분석
- Zandbergen, R. "Radio-carbon dating of the Voynich MS." voynich.nu. <https://www.voynich.nu/extra/carbon.html>
- McCrone Associates, ink/pigment analysis (cited in Beinecke 자료).

## 종합 자료
- "Voynich manuscript". *Wikipedia*. <https://en.wikipedia.org/wiki/Voynich_manuscript>
- voynich.nu (René Zandbergen 운영). <https://www.voynich.nu/>

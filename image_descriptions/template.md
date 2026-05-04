# 폴리오 이미지 설명 — 표준 템플릿

> **사용법**: 이 파일을 복사해 `<section>/f<번호><r|v>.md`로 저장한 뒤 채운다.
> 빈 항목은 `N/A`로 표기. 추측은 비워두는 게 낫다.

```yaml
---
folio_id: f___          # 예: f2v, f67r1
section: ___            # herbal | astronomical | cosmological | zodiac | biological | pharmaceutical | recipes
currier_lang: ___       # A | B (RF1b-e.txt 헤더 $L 값)
scribe: ___             # 1–5 (헤더 $H 값)
illustration_type: ___  # IVTFF $I 코드
foldout: false          # 접지(폴드아웃) 여부
beinecke_url: ___       # https://collections.library.yale.edu/...
inspected_date: 2026-__-__
inspector: ___          # 작성자
---
```

## 1. 페이지 전체 구성

- **레이아웃 방향**: 세로 / 가로 / 폴드아웃 (___ 면 펼침)
- **이미지 영역의 비율**: 페이지 면적 중 약 ___% (대략적)
- **텍스트 블록 개수**: ___ 개
- **이미지와 텍스트의 배치 관계**:
  - [ ] 이미지가 페이지 중앙, 텍스트가 둘러쌈
  - [ ] 이미지가 상단/하단, 텍스트가 반대편
  - [ ] 텍스트가 이미지 외곽선을 따라 흐름 (text-avoiding)
  - [ ] 이미지 내부에 라벨(짧은 단어)이 박혀 있음
  - [ ] 기타: ___

## 2. 색상 팔레트

페이지에 나타나는 색의 종류와 사용 위치 (이미지 보고 그대로):

| 색 | 사용된 영역 |
|----|-------------|
| 갈색/적갈색 | (예: 잉크, 줄기) |
| 녹색 | |
| 파랑 | |
| 빨강 | |
| 노랑/황토 | |
| 검정 | |
| 기타 | |

## 3. 이미지 객체 인벤토리 (관찰만)

> **규칙**: "이게 뭐다"가 아니라 "이런 모양의 것이 N개" 형태로 기록.

### 객체 1
- **위치**: 페이지의 ___ (예: 중앙, 상단 좌측)
- **크기 (상대)**: 페이지 가로/세로 대비 ___%
- **형태 요소**:
  - 줄기/축: 있음/없음, 직선/곡선, 분기 N회
  - 잎 모양 구조: ___장, 형태 (계란형/타원/창형/장상/우상/...), 잎가장자리 (매끈/톱니/...)
  - 꽃 모양 구조: ___개, 꽃잎 ___장, 색 ___
  - 뿌리 모양 구조: 형태 (수염/덩이/구근), 색
  - 기타 부속: ___
- **라벨**: 객체에 붙은 짧은 단어가 있는가? 있으면 EVA 인용 (예: `okeoeey`)

### 객체 2
(반복)

## 4. 라벨 단어 (있는 경우)

| 위치 | EVA 텍스트 | 라벨이 가리키는 객체 (관찰적) |
|------|-----------|------------------------------|
| | | |

## 5. 텍스트 블록

| 블록 # | 위치 | 라인 수 | 시작 단어 (EVA) | RF1b-e.txt에서의 라인 ID |
|--------|------|---------|----------------|--------------------------|
| 1 | 상단 | | | f___.1 ~ f___.N |
| 2 | | | | |

## 6. 특이 관찰

- 다른 페이지와 명백히 공유되는 모티프: ___
- 손상/얼룩/주석/이후 가필: ___
- 비대칭/대칭성: ___

## 7. 정량 요약 (Phase 5 매핑용 특성 벡터 후보)

> 이 항목은 임베딩 입력으로 직접 쓰일 수치 특성. 추측 없이 *센 것*만.

```yaml
n_text_blocks: ___
n_distinct_objects: ___
n_labels: ___
n_colors_used: ___
has_circular_structure: false
has_radial_symmetry: false
has_human_figure: false
has_container: false
plant_features:
  n_leaves_visible: ___
  n_flowers_visible: ___
  has_root: ___
  branching_depth: ___
astronomical_features:
  n_stars: ___
  n_concentric_rings: ___
  has_sun_face: false
  has_moon_face: false
```

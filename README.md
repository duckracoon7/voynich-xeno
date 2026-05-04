# voynich-xeno

Voynich 필사본(Beinecke MS 408)을 **비(非)지구 유래 언어**라는 가정하에 해독을 시도하는 연구 저장소.

## 가설

기존 연구는 보이니치를 *사어(死語)* 로 가정하고 고대 언어와의 유사성으로 접근. 본 저장소는 그 가정을 *배제*하고:

- 문화·언어 체계가 우리의 이해와 *완전히 다를 수 있다*는 전제
- 관찰 가능한 두 가지: **체계 모를 문자의 나열** + **이미지**
- 따라서 **이미지와 문자를 매핑**하는 길을 모색

자세한 가설 정리와 선행연구 비교는 [`voynich_research_notes.md`](voynich_research_notes.md), 실행 계획은 [`voynich_research_plan.md`](voynich_research_plan.md).

## 디렉터리

```
voynich-xeno/
├── voynich_research_notes.md     # 가설 + 선행 연구 조사 (출처 포함)
├── voynich_research_plan.md      # 5-Phase 실행 계획서
├── data/                         # EVA 전사본 (voynich.nu 출처)
│   ├── README.md                 # IVTFF 2.0 형식 가이드
│   ├── RF1b-e.txt                # Reference Extended EVA (권장 기본)
│   ├── RF1b-er.txt               # Reference Basic EVA
│   ├── IT2a-n.txt                # Takahashi EVA
│   ├── ZL3b-n.txt                # Zandbergen-Landini EVA
│   └── CD2a-n.txt                # Currier 표기
├── image_descriptions/           # 226개 폴리오의 이미지 관찰 문서
│   ├── README.md                 # 작성 원칙(P4: 동정 금지)
│   ├── template.md               # 표준 템플릿
│   ├── section_inventory.md      # 섹션별 폴리오 인벤토리
│   ├── generate_skeleton.py      # 스켈레톤 생성기
│   ├── astronomical/             # 8 페이지
│   ├── biological/               # 19 페이지
│   ├── cosmological/             # 10 페이지
│   ├── herbal/                   # 129 페이지 (5 detail + 124 placeholder)
│   ├── pharmaceutical/           # 16 페이지
│   ├── recipes/                  # 25 페이지
│   ├── text/                     # 7 페이지
│   └── zodiac/                   # 12 페이지
└── scans/                        # (gitignored) 원본 PDF + 페이지별 JPG
```

## 진행 상황

- [x] EVA 전사본 확보 + 검증 (Currier A/B 분포가 1976년 원본과 부합)
- [x] 226개 폴리오 스켈레톤 자동 생성 (IVTFF locator 기반 라벨/본문 분리)
- [x] 226개 페이지 직접 관찰 작성 (Beinecke MS 408 공식 PDF 기반)
  - **상세 관찰 102개**: astronomical 8 / biological 19 / cosmological 10 / pharmaceutical 16 / recipes 25 / text 7 / zodiac 12 / herbal 5
  - **generic placeholder 124개**: herbal 페이지 (메타데이터 보존, 정밀 카운트는 후속 작업)
- [ ] Phase 2: 통계 베이스라인 재현 (Bowern & Lindemann의 h₂ ≈ 2 검증)
- [ ] Phase 3: 임베딩 공간 구축
- [ ] Phase 4: 내적 검증 (holdout / 비지도 군집)
- [ ] Phase 5: 이미지-텍스트 매핑

## 데이터 출처

- **EVA 전사**: <https://www.voynich.nu/transcr.html> (René Zandbergen)
- **원본 스캔**: Yale University Beinecke Rare Book and Manuscript Library, MS 408. <https://collections.library.yale.edu/catalog/2002046>

## 핵심 원칙 (계획서 §0)

- **P1**: EVA 표기를 자체 표기 대신 차용
- **P2**: Currier A/B 분리 모델링
- **P3**: 모든 평가는 holdout 폴리오 기준
- **P4**: 이미지를 ground truth로 쓰지 않음 (Cheshire 2019 함정 회피)
- **P5**: 재현 가능한 시드와 코드
- **P6**: 단일 모델 결론 금지, 2개 독립 메서드 합의 시 채택

## 누락 폴리오

원본 116 folio 중 14개 분실 (작업 제외): f12, f59–f64, f74, f91–f92, f97–f98, f109–f110.

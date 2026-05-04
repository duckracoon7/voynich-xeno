# Voynich Manuscript - EVA 전사본 데이터

> 출처: <https://www.voynich.nu/transcr.html> (René Zandbergen 운영)
> 다운로드 일자: 2026-05-04
> 형식: IVTFF 2.0 (Intermediate Voynich Transliteration File Format)

## 파일 목록

| 파일 | 코드 | 형식 | 크기 | 설명 |
|------|------|------|------|------|
| `RF1b-e.txt` | RF (Reference) | Extended EVA | 362 KB | **권장 기본 파일**. 모든 글리프 포함. ZL+GC 자동 결합 |
| `RF1b-er.txt` | RF (Reference) | Basic EVA | 344 KB | 희귀 글리프 단순화된 기본 EVA |
| `IT2a-n.txt` | IT (Takahashi) | EVA | 342 KB | Takeshi Takahashi의 손수 검증 전사 |
| `ZL3b-n.txt` | ZL (Zandbergen-Landini) | EVA | 412 KB | EVA 설계자들의 전사 |
| `CD2a-n.txt` | CD (Currier-D'Imperio) | Currier | 133 KB | 비교용. EVA 아닌 Currier 표기 |

## 구조 요약 (RF1b-e.txt 기준)

- **총 라인 수**: 5,613
- **폴리오 페이지 수**: 184
- **Currier A 페이지**: 102
- **Currier B 페이지**: 72
- **필경사(Scribe) 분포**: H1=101, H2=40, H3=29, H4=6, H5=7

> ※ Currier 1976 원본의 114/83과 약간 다름 — RF가 텍스트가 있는 폴리오만 커버하기 때문.

## IVTFF 폴리오 헤더 메타데이터

각 폴리오 시작 라인 예시:
```
<f1r>      <! $Q=A $P=A $F=a $B=1 $I=T $L=A $H=1 $C=1 $X=V>
```

| 필드 | 의미 | 값 예시 |
|------|------|---------|
| `<f1r>` | folio ID (앞면 r=recto, 뒷면 v=verso) | f1r, f1v, f2r... |
| `$Q` | quire (제본 단위) | A, B, C... |
| `$P` | 페이지 번호 (quire 내) | A, B, C... |
| `$F` | folio 번호 (quire 내) | a, b, c... |
| `$B` | 단순 페이지 카운트 | 1, 2, 3... |
| `$I` | 일러스트 타입 | T(text-only), H(herbal), A(astro), B(bio)... |
| `$L` | **Currier 언어** | **A 또는 B** |
| `$H` | **필경사(scribe)** | 1–5 |
| `$C` | currier hand variant | 1, 2... |
| `$X` | 기타 표식 | V, C, O... |

## 라인 데이터 형식

```
<f1r.1,@P0>       fachys.ykal.ar.@221;taiin.shol.shory.{cto}ses.y.kor.sholdy
```

- `<f1r.1>`: folio f1r, 라인 1
- `@P0`: 단락 종류 (P0 = 일반 본문)
- `+P0` = 같은 단락 연속, `=Pt` = 제목, `*P0` = 새 단락 시작, `@Lp` = 라벨
- 본문에서:
  - `.` = 단어 구분자
  - `,` = 약한 단어 구분 (불확실)
  - `<->` = 큰 갭 (그림 등으로 인한 분리)
  - `@221;` = 희귀 글리프 (숫자 코드)
  - `{cto}` = 글리프 클러스터
  - `?` = 판독 불가
  - `'` = 특수 변형

## 사용 권장사항

- **분석 기본**: `RF1b-e.txt` (가장 완비)
- **재현성 확인**: `IT2a-n.txt`와 교차 검증
- **Currier A/B 분리 학습**: 폴리오 헤더 `$L` 필드로 분기
- **필경사별 분리**: 정밀 분석 시 `$H` 필드로도 분기

## 일러스트 섹션 코드 (`$I`) 참고

| 코드 | 섹션 |
|------|------|
| `T` | text-only |
| `H` | herbal (식물) |
| `A` | astronomical (천문) |
| `Z` | zodiac (별자리) |
| `B` | biological (생물/목욕) |
| `C` | cosmological (우주) |
| `P` | pharmaceutical (약초) |
| `S` | stars (recipes) |

연구 계획서 Phase 1의 코퍼스 정규화 시 이 메타데이터를 그대로 활용.

# f1v — 추정 재구성 번역 (Speculative Reconstruction)

> ⚠️ **이것은 결정론적 번역이 아니다.**
>
> 각 토큰을 그 *시각적 anchor*로 치환한 재구성. 의미는 영영 모를 수 있음.
> 신뢰도 표지: ★ NPMI≥0.4, ✦ NPMI≥0.25, ☆ 약함, ? 미상
>
> ⟪이중꺾쇠⟫ = 라벨 위치 (명사 가능성 높음)
> ⟨꺾쇠⟩ = UNK 또는 anchor 없음

## EVA 원문

```
  L  1 [@P0]: kchsy.chodaiin.ol<->oltchey.char.cfhar.am
  L  2 [+P0]: yteey.char.or.ochy<->dcho.lkody.okodar.chody
  L  3 [+P0]: do.ckhy.ckhockhy.{ch'}y<->dksheey.cthy.kotchody.dal
  L  4 [+P0]: dol.chokeo.dair.dam<->sochey.cho,kody
  L  5 [+P0]: potoy.shol.jair.cphoal<->dar.chey.tody.otoaiin.shoshy
  L  6 [+P0]: choky.chol.ctholshol.@221;kal<->@152;olchey.chodo.lol.chy.cthy
  L  7 [+P0]: qo.ol.choees.cheol.dol.cthey<->ykol.dol.dolo.ykol.dolchiody
  L  8 [+P0]: okolshol.kol.kechy.chol.ky<->chol.cthol.chody.chol.daiin
  L  9 [+P0]: shor.okal.chol.dolky.dar<->shol.dchor.otcho.dar.shody
  L 10 [+P0]: toor.chotchey.dal.chody<->schody.pol.chodar
```

## 한국어 추정 재구성

```
  L  1: ⟨kchsy⟩ 장식☆ 단락✦ ⟨oltchey⟩ 장식★ ⟨cfhar⟩ 단락✦
  L  2: 중심별★ 장식★ 장식☆ 꽃★ 꽃★ ⟨lkody⟩ ⟨okodar⟩ 단락☆
  L  3: 꽃★ 꽃✦ ⟨ckhockhy⟩ 꽃★ ⟨dksheey⟩ 글단✦ ⟨kotchody⟩ 물✦
  L  4: 사람✦ ⟨chokeo⟩ 단락✦ 꽃잎✦ ⟨sochey⟩ 장식☆ 마진주석✦
  L  5: ⟨potoy⟩ ⟨shol⟩☆ ⟨jair⟩ ⟨cphoal⟩ ⟨dar⟩☆ 장식✦ 꽃★ ⟨otoaiin⟩ ⟨shoshy⟩
  L  6: 용기✦ 장식☆ ⟨ctholshol⟩ 꽃★ ⟨@152;olchey⟩ ⟨chodo⟩ 사람★ 꽃☆ 글단✦
  L  7: 단락✦ 단락✦ ⟨choees⟩ 단락✦ 사람✦ 식물조각✦ 마진주석✦ 사람✦ ⟨dolo⟩ 마진주석✦ ⟨dolchiody⟩
  L  8: ⟨okolshol⟩ 별표★ ⟨kechy⟩ 장식☆ 단락✦ 장식☆ 글단✦ 단락☆ 장식☆ 그것☆
  L  9: 용기☆ 단락✦ 장식☆ ⟨dolky⟩ ⟨dar⟩☆ ⟨shol⟩☆ 객체☆ 꽃✦ ⟨dar⟩☆ 장식☆
  L 10: ⟨toor⟩ ⟨chotchey⟩ 물✦ 단락☆ ⟨schody⟩ 풀★ 별✦
```

## English speculative reconstruction

```
  L  1: ⟨kchsy⟩ ornament☆ para✦ ⟨oltchey⟩ ornament★ ⟨cfhar⟩ para✦
  L  2: center-star★ ornament★ ornament☆ flower★ flower★ ⟨lkody⟩ ⟨okodar⟩ para☆
  L  3: flower★ flower✦ ⟨ckhockhy⟩ flower★ ⟨dksheey⟩ column✦ ⟨kotchody⟩ water✦
  L  4: person✦ ⟨chokeo⟩ para✦ petal✦ ⟨sochey⟩ ornament☆ margin-note✦
  L  5: ⟨potoy⟩ ⟨shol⟩☆ ⟨jair⟩ ⟨cphoal⟩ ⟨dar⟩☆ ornament✦ flower★ ⟨otoaiin⟩ ⟨shoshy⟩
  L  6: vessel✦ ornament☆ ⟨ctholshol⟩ flower★ ⟨@152;olchey⟩ ⟨chodo⟩ person★ flower☆ column✦
  L  7: para✦ para✦ ⟨choees⟩ para✦ person✦ plant-part✦ margin-note✦ person✦ ⟨dolo⟩ margin-note✦ ⟨dolchiody⟩
  L  8: ⟨okolshol⟩ star★ ⟨kechy⟩ ornament☆ para✦ ornament☆ column✦ para☆ ornament☆ (it)☆
  L  9: vessel☆ para✦ ornament☆ ⟨dolky⟩ ⟨dar⟩☆ ⟨shol⟩☆ object☆ flower✦ ⟨dar⟩☆ ornament☆
  L 10: ⟨toor⟩ ⟨chotchey⟩ water✦ para☆ ⟨schody⟩ pool★ star✦
```

## 면책

- 이 번역은 *외부 ground truth* 없이 *우리 자신의 이미지 노트*에서 도출됨 (자기 입력 의존).
- 토큰 → anchor → 의미 후보의 매핑은 통계적으로 유의 (Phase 9 순열검정 50/50 p<0.01)이지만,
  *anchor 자체의 의미는 추측*임. "사람"이 정말 "사람"을 가리킨다는 보장 없음.
- hapax 6,760개는 무시됨 (사전에 없음).

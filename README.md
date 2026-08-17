# Ontology Workshop

HR 규정 문서로 검색의 한계 → 위키 → 온톨로지로 이어지는 실습 저장소.

## 구성

- `docs/` — 규정 원본 10편. 모든 실습의 공용 원천. 수정하지 않는다.
- `new-sources/` — 실습 3에서 위키에 주입할 새 문서.
- `wiki/` — 실습 산출물이 누적되는 연속 작업 공간. `setup_wiki.py` 가 만든다. (git 미추적)
- `week1/` — 실습 1 도구.

## 실습 1 — 검색과 링크 (week1/)

규정을 조항 조각으로 나눠 색인으로 찾고, 조항 인용을 링크로 바꿔
검색이 문서 사이의 화살표를 따라가게 한다.

    cd week1
    python3 split.py      # 조항 단위 조각
    python3 index.py      # 색인 한 장
    python3 ask.py "연장근로 규칙 알려줘"
    python3 link.py       # 인용 → 링크. 이후 ask.py 가 링크를 따라간다

## 실습 2 — 첫 위키

규정 전부를 sources/ 로 복사한 위키 실습장을 만들고,
위키 규칙(CLAUDE.md)을 직접 작성한 뒤 Claude Code 에게 개념 페이지 생성을 요청한다.

    python3 setup_wiki.py
    # wiki/CLAUDE.md 를 직접 만들어 위키 규칙을 붙여 넣는다
    cd wiki && claude
    python3 validate_wiki.py

## 실습 3 — 지식 병합

new-sources/ 의 문서를 wiki/sources/ 로 직접 옮기고,
기존 페이지 갱신·신규 생성·보류를 구분하게 한다. 결과는 git diff 로 리뷰한다.

## 실습 사이의 연속성

각 실습을 마치면 wiki 안에서 커밋해 다음 실습의 기준선을 남긴다.

    git -C wiki add -A && git -C wiki commit -m "실습 N 완료"

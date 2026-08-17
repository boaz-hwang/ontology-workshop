# Ontology Workshop

HR 규정 문서로 검색의 한계 → 위키 → 온톨로지로 이어지는 실습 저장소.

## 구성

- `docs/` — 규정 원본 10편. 모든 실습의 공용 원천. 수정하지 않는다.
- `new-sources/` — 실습 3에서 위키에 주입할 새 문서.
- `wiki/` — 실습 산출물이 누적되는 연속 작업 공간. `setup_wiki.py` 가 만든다. (git 미추적)
- `week1/` — 실습 1 도구.

## 실습 1 — RAG 파이프라인 (week1/)

문서가 조각·숫자·색인을 거쳐 답변이 되는 과정을 한 단계씩 실행하며
단계마다 산출물 파일을 직접 열어 눈으로 확인한다.

    cd week1
    python3 split.py        # ① 글 → 조각          (chunks/ 105개 파일)
    python3 embedding.py    # ② 조각 → 숫자(벡터)   (vectors/ 105개 파일)
    python3 indexing.py     # ③ 숫자 → 색인 한 장   (vectors.tsv)
    python3 ask.py "시간외근로수당 기준 알려줘"   # ④ 질문 → 숫자 → 거리 → 답변
    python3 link.py         # ⑤ 조각 속 인용 → 링크. 이후 ask.py 가 링크를 따라간다

관찰 포인트:

- "시간외근로수당"은 문서에 없는 표현이지만 거리 계산으로 연장근로수당 조각이 잡힌다.
- "잔업하면 돈 더 줘?" 는 사전 밖 어휘라 벡터가 되지 못한다 — 임베딩의 지식은 사전(모델)이 결정한다.
- "연차 쓰다 남으면?" 은 맞는 문서 근처까지만 간다 — 가깝다는 것이 정답 조항을 보장하지 않는다.

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

"""
index.py — 조각들을 미리 훑어 '색인'을 만든다.

    python3 index.py

질문하기 전에 딱 한 번 실행한다.
조각 하나하나를 열어보는 대신, 이 색인 한 장만 보면 어느 조각을 열어야 하는지 알 수 있다.
색인은 index.tsv 에 저장되며, 메모장으로 열어서 눈으로 확인할 수 있다.
"""
import re
from collections import Counter
from pathlib import Path

조각폴더 = Path("chunks")
색인파일 = Path("index.tsv")

# 어느 조항에나 나와서 조각을 구분하는 데 도움이 안 되는 말들
흔한말 = {
    "규정", "규칙", "경우", "직원", "회사", "이하", "이상", "이내", "해당", "다음",
    "각호", "제외", "포함", "대하여", "관한", "관하여", "따라", "따른", "위하여",
    "하여야", "하지", "아니한다", "있다", "한다", "본다", "목적", "적용", "사항",
}


# 한국어는 단어 뒤에 조사가 붙는다. '회사가'와 '회사를'을 같은 말로 보려면 떼어내야 한다.
조사목록 = sorted(
    ["으로써", "에서는", "에게는", "으로는", "에서", "에게", "으로", "이라", "까지",
     "부터", "보다", "마다", "이나", "라도", "은", "는", "이", "가", "을", "를",
     "에", "의", "로", "와", "과", "도", "만"],
    key=len, reverse=True,
)


def 조사떼기(단어: str) -> str:
    for 조사 in 조사목록:
        if 단어.endswith(조사) and len(단어) - len(조사) >= 2:
            return 단어[: -len(조사)]
    return 단어


def 조항제목(본문: str) -> str:
    """조각 안의 '## 제3조 (사전승인 원칙)' 같은 줄을 찾아 제목으로 쓴다."""
    for 줄 in 본문.splitlines():
        if 줄.startswith("## "):
            return 줄[3:].strip()
    return 본문.splitlines()[0].strip()


줄들 = []
for 조각 in sorted(조각폴더.glob("*.md")):
    본문 = 조각.read_text(encoding="utf-8")

    # 한글 두 글자 이상만 뽑아서 몇 번 나왔는지 센다
    # 조사를 뗀 형태와 원래 형태를 모두 넣는다. ('연차유급휴가'가 '연차유급휴'로 깎이는 것을 막는다)
    뽑은단어 = re.findall(r"[가-힣]{2,}", 본문)
    단어들 = [단어 for 단어 in 뽑은단어 + [조사떼기(단어) for 단어 in 뽑은단어]
              if len(단어) >= 2 and 단어 not in 흔한말]
    핵심단어 = [단어 for 단어, _ in Counter(단어들).most_common(8)]

    줄들.append(f"{조각.name}\t{조항제목(본문)}\t{','.join(핵심단어)}")

색인파일.write_text("\n".join(줄들) + "\n", encoding="utf-8")

print(f"조각 {len(줄들)}개  →  색인 1장 ({색인파일}, {색인파일.stat().st_size:,}바이트)")
print()
print("색인 미리보기 (앞 3줄):")
for 줄 in 줄들[:3]:
    파일, 제목, 단어 = 줄.split("\t")
    print(f"  {파일}  |  {제목}  |  {단어}")

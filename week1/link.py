"""
link.py — 문서에 글로만 적혀 있는 조항 인용을 진짜 링크로 바꾼다.

    python3 link.py          바꿀 곳을 보여주기만 한다 (문서는 그대로)
    python3 link.py --적용    docs/ 문서에 링크를 써넣는다

규정 문서는 서로를 가리킨다. "별표 1에서 정하는 바에 따른다" 같은 문장이 그것이다.
사람은 그 말을 보고 별표 1을 찾아가지만, 검색은 그 화살표를 따라가지 못한다.
이 코드는 문장에 적힌 인용을 컴퓨터가 따라갈 수 있는 링크로 바꾼다. 문장 자체는 바꾸지 않는다.
"""
import re
import sys
from pathlib import Path

원본폴더 = Path("docs")

# 「연장근로 및 휴일근로 운영규정」 별표 1   /   같은 규정 제3조   /   제5조
인용찾기 = re.compile(
    r"「(?P<규정>[^」]+)」\s*(?P<타규정조항>별표\s*\d+|제\d+조)"
    r"|같은\s*규정\s*(?P<앞규정조항>별표\s*\d+|제\d+조)"
    r"|(?P<이문서조항>제\d+조)"
)
이미링크 = re.compile(r"\[[^\]]*\]\([^)]*\)")


def 앵커(조항제목: str) -> str:
    """'제3조 (사전승인 원칙)' → '제3조-사전승인-원칙'"""
    s = re.sub(r"[^\w\s-]", "", 조항제목.strip().lower())
    return re.sub(r"\s+", "-", s)


def 조항키(텍스트: str) -> str:
    """'별표 1' 과 '별표1' 을 같은 것으로 본다."""
    return re.sub(r"\s+", "", 텍스트)


# ── 1. 어떤 문서에 어떤 조항이 있는지 먼저 모은다 ──────────────────
문서제목별파일 = {}   # '연장근로 및 휴일근로 운영규정' → '03-연장근로.md'
조항주소 = {}         # ('03-연장근로.md', '별표1') → '03-연장근로.md#별표-1-연장근로-가산율'

for 문서 in sorted(원본폴더.glob("*.md")):
    for 줄 in 문서.read_text(encoding="utf-8").splitlines():
        if 줄.startswith("# "):
            문서제목별파일[줄[2:].strip()] = 문서.name
        elif 줄.startswith("## "):
            제목 = 줄[3:].strip()
            머리 = re.match(r"(별표\s*\d+|제\d+조)", 제목)
            if 머리:
                조항주소[(문서.name, 조항키(머리.group(1)))] = f"{문서.name}#{앵커(제목)}"


# ── 2. 문서를 한 줄씩 보며 인용을 링크로 바꾼다 ────────────────────
def 링크걸기(줄, 이파일, 직전규정파일):
    바뀐것 = []

    def 치환(m):
        nonlocal 직전규정파일
        if m.group("타규정조항"):
            대상파일 = 문서제목별파일.get(m.group("규정").strip())
            조항 = m.group("타규정조항")
            직전규정파일 = 대상파일 or 직전규정파일
            앞말 = f"「{m.group('규정')}」 "
        elif m.group("앞규정조항"):
            대상파일 = 직전규정파일
            조항 = m.group("앞규정조항")
            앞말 = "같은 규정 "
        else:
            대상파일 = 이파일
            조항 = m.group("이문서조항")
            앞말 = ""

        주소 = 조항주소.get((대상파일, 조항키(조항))) if 대상파일 else None
        if not 주소:
            return m.group(0)
        바뀐것.append((조항, 주소))
        return f"{앞말}[{조항}]({주소})"

    # 이미 링크인 부분은 건드리지 않는다
    조각들 = 이미링크.split(줄)
    링크들 = 이미링크.findall(줄)
    조각들 = [인용찾기.sub(치환, 조각) for 조각 in 조각들]

    결과 = 조각들[0]
    for 링크, 조각 in zip(링크들, 조각들[1:]):
        결과 += 링크 + 조각
    return 결과, 바뀐것, 직전규정파일


적용 = "--적용" in sys.argv
전체 = 0

for 문서 in sorted(원본폴더.glob("*.md")):
    줄들 = 문서.read_text(encoding="utf-8").splitlines()
    새줄들, 문서변경, 직전규정파일 = [], [], None

    for 번호, 줄 in enumerate(줄들, start=1):
        if 줄.startswith("#"):          # 제목 줄은 그대로 둔다
            새줄들.append(줄)
            continue
        새줄, 바뀐것, 직전규정파일 = 링크걸기(줄, 문서.name, 직전규정파일)
        새줄들.append(새줄)
        문서변경 += [(번호, 조항, 주소) for 조항, 주소 in 바뀐것]

    if 문서변경:
        print(f"{문서.name}")
        for 번호, 조항, 주소 in 문서변경:
            print(f"  {번호:>3}행  {조항:<8} → {주소}")
        전체 += len(문서변경)
        if 적용:
            문서.write_text("\n".join(새줄들) + "\n", encoding="utf-8")

print()
if 적용:
    print(f"링크 {전체}곳을 문서에 써넣었습니다. split.py 와 index.py 를 다시 실행하세요.")
else:
    print(f"링크로 바꿀 곳 {전체}곳을 찾았습니다. 실제로 바꾸려면 --적용 을 붙이세요.")

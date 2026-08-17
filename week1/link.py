"""
link.py — 조각에 글로만 적혀 있는 조항 인용을 진짜 링크로 바꾼다.

    python3 link.py

split.py 가 만든 chunks/ 조각에 링크를 써넣는다.
저장소 루트 docs/ 원본 문서는 건드리지 않는다.

규정 문서는 서로를 가리킨다. "별표 1에서 정하는 바에 따른다" 같은 문장이 그것이다.
사람은 그 말을 보고 별표 1을 찾아가지만, 검색은 그 화살표를 따라가지 못한다.
이 코드는 조각에 적힌 인용을 컴퓨터가 따라갈 수 있는 링크로 바꾼다. 문장 자체는 바꾸지 않는다.

split.py 를 다시 실행하면 조각이 새로 만들어져 링크가 사라진다.
그때는 link.py 를 다시 실행한다.
"""
import re
import sys
from pathlib import Path

원본폴더 = Path("../docs")
조각폴더 = Path("chunks")

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


# ── 2. 조각을 한 줄씩 보며 인용을 링크로 바꾼다 ────────────────────
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


조각목록 = sorted(조각폴더.glob("*.md"))
if not 조각목록:
    sys.exit("chunks/ 가 비어 있습니다. 먼저 python3 split.py 를 실행하세요.")

전체 = 0

for 조각 in 조각목록:
    이파일 = 조각.stem.rsplit("-", 1)[0] + ".md"
    줄들 = 조각.read_text(encoding="utf-8").splitlines()
    새줄들, 조각변경, 직전규정파일 = [], [], None

    for 줄 in 줄들:
        if 줄.startswith("#"):          # 제목 줄은 그대로 둔다
            새줄들.append(줄)
            continue
        새줄, 바뀐것, 직전규정파일 = 링크걸기(줄, 이파일, 직전규정파일)
        새줄들.append(새줄)
        조각변경 += 바뀐것

    if 조각변경:
        print(f"{조각.name}")
        for 조항, 주소 in 조각변경:
            print(f"  {조항:<8} → {주소}")
        전체 += len(조각변경)
        조각.write_text("\n".join(새줄들) + "\n", encoding="utf-8")

print()
if 전체:
    print(f"링크 {전체}곳을 조각에 써넣었습니다. (docs/ 원본은 그대로입니다)")
else:
    print("새로 바꿀 인용이 없습니다. (이미 링크가 걸려 있습니다)")

"""
ask.py — 색인으로 조각을 찾아서, 찾은 조각만 AI에게 준다.

    python3 ask.py "연장근로 규칙 알려줘"          색인으로 찾기 (RAG)
    python3 ask.py --전체 "연장근로 규칙 알려줘"    비교용: 문서 10장을 통째로 넘기기
    python3 ask.py --답변 "연장근로 규칙 알려줘"    찾은 조각으로 실제 답변까지

열어본 파일 수와 AI에게 넘긴 글자 수를 함께 보여준다.
"""
import subprocess
import sys
from pathlib import Path

색인파일 = Path("index.tsv")
조각폴더 = Path("chunks")
원본폴더 = Path("docs")

흔한말 = {"규칙", "규정", "알려줘", "뭐야", "어떻게", "얼마", "기준", "내용", "관련", "설명"}
뽑을조각수 = 3


def 검색(질문):
    """색인 한 장만 읽고, 질문의 단어가 많이 들어간 조각을 고른다."""
    검색어 = [단어 for 단어 in 질문.split() if len(단어) >= 2 and 단어 not in 흔한말]

    점수표 = []
    for 줄 in 색인파일.read_text(encoding="utf-8").splitlines():
        파일명, 제목, 핵심단어 = 줄.split("\t")
        찾을곳 = 제목 + " " + 핵심단어
        점수 = sum(찾을곳.count(단어) for 단어 in 검색어)
        if 점수:
            점수표.append((점수, 파일명, 제목))

    점수표.sort(reverse=True)
    return 검색어, 점수표[:뽑을조각수]


def 물어보기(근거, 질문):
    """찾은 근거만 주고 답하게 한다."""
    프롬프트 = f"아래 근거로만 한국어로 답해줘. 근거에 없으면 없다고 말해줘.\n\n[근거]\n{근거}\n\n[질문] {질문}"
    결과 = subprocess.run(
        ["claude", "-p", 프롬프트, "--allowed-tools", "", "--output-format", "text"],
        capture_output=True, text=True,
    )
    return 결과.stdout.strip()


인자 = sys.argv[1:]
전체모드 = "--전체" in 인자
답변모드 = "--답변" in 인자
질문 = " ".join(a for a in 인자 if not a.startswith("--")) or "연장근로 규칙 알려줘"

print(f"[질문] {질문}\n")

if 전체모드:
    파일들 = sorted(원본폴더.glob("*.md"))
    근거 = "\n\n".join(f.read_text(encoding="utf-8") for f in 파일들)
    print(f"방식: 문서를 통째로 넘긴다 (검색 없음)")
    print(f"  열어본 파일 : {len(파일들)}개  (docs/ 전부)")
    print(f"  넘긴 글자   : {len(근거):,}자")
else:
    검색어, 히트 = 검색(질문)
    print(f"방식: 색인으로 찾는다")
    print(f"  검색어      : {검색어}")
    if not 히트:
        print(f"  찾은 조각   : 0개  ← 색인에 이 단어가 없습니다")
        print(f"  열어본 파일 : 1개  (index.tsv 만)")
        print(f"  넘긴 글자   : 0자")
        print(f"\n[답변] 관련 내용을 찾지 못했습니다.")
        sys.exit()
    for 점수, 파일명, 제목 in 히트:
        print(f"     {점수}점  {파일명}  {제목}")
    근거 = "\n\n".join((조각폴더 / 파일명).read_text(encoding="utf-8") for _, 파일명, _ in 히트)
    print(f"  열어본 파일 : {1 + len(히트)}개  (index.tsv 1 + 조각 {len(히트)})")
    print(f"  넘긴 글자   : {len(근거):,}자")

if 답변모드:
    print(f"\n[답변] {물어보기(근거, 질문)}")

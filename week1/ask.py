"""
ask.py — 색인으로 조각을 찾아서, 찾은 조각만 AI에게 준다.

    python3 ask.py "연장근로 규칙 알려줘"
    python3 ask.py --검색만 "연장근로 규칙 알려줘"    AI를 부르지 않고 검색 결과만 본다

열어본 파일 수와 AI에게 넘긴 글자 수, 그리고 AI 호출에 든 비용을 함께 보여준다.
AI 호출에는 로그인된 claude CLI가 필요하다.
"""
import json
import subprocess
import sys
from pathlib import Path

색인파일 = Path("index.tsv")
조각폴더 = Path("chunks")

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
    프롬프트 = (f"아래 근거로만 한국어로 답해줘. 근거에 없으면 없다고 말해줘.\n\n"
                f"[근거]\n{근거}\n\n[질문] {질문}")
    결과 = subprocess.run(
        ["claude", "-p", 프롬프트, "--allowed-tools", "", "--output-format", "json"],
        capture_output=True, text=True,
    )
    응답 = json.loads(결과.stdout)
    사용량 = 응답.get("usage", {})
    읽은토큰 = (사용량.get("input_tokens", 0)
                + 사용량.get("cache_read_input_tokens", 0)
                + 사용량.get("cache_creation_input_tokens", 0))
    return 응답.get("result", "").strip(), 응답.get("num_turns", 0), 읽은토큰, 응답.get("duration_ms", 0) / 1000


인자 = sys.argv[1:]
검색만 = "--검색만" in 인자
질문 = " ".join(a for a in 인자 if not a.startswith("--")) or "연장근로 규칙 알려줘"

print(f"[질문] {질문}\n")

검색어, 히트 = 검색(질문)
print(f"  검색어      : {검색어}")

if not 히트:
    print("  찾은 조각   : 0개  ← 색인에 이 단어가 없습니다")
    print("  열어본 파일 : 1개  (index.tsv 만)")
    print("  넘긴 글자   : 0자")
    print("\n[답변] 관련 내용을 찾지 못했습니다.")
    sys.exit()

for 점수, 파일명, 제목 in 히트:
    print(f"     {점수}점  {파일명}  {제목}")

근거 = "\n\n".join((조각폴더 / 파일명).read_text(encoding="utf-8") for _, 파일명, _ in 히트)
print(f"  열어본 파일 : {1 + len(히트)}개  (index.tsv 1 + 조각 {len(히트)})")
print(f"  넘긴 글자   : {len(근거):,}자")

if 검색만:
    print("\n(AI 호출은 건너뛰었습니다)")
    sys.exit()

답변, 턴, 읽은토큰, 초 = 물어보기(근거, 질문)
print("  ── AI 호출 ──")
print(f"  대화 턴     : {턴}회")
print(f"  읽은 토큰   : {읽은토큰:,}")
print(f"  걸린 시간   : {초:.1f}초")
print(f"\n[답변] {답변}")

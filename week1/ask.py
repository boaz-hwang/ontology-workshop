"""
ask.py — 같은 질문을 두 가지 방식으로 처리하고, 든 비용을 비교한다.

    python3 ask.py --그냥 "연장근로 규칙 알려줘"    Claude Code에게 폴더째 맡긴다 (검색 코드 없음)
    python3 ask.py "연장근로 규칙 알려줘"           색인으로 조각을 찾아, 그 조각만 넘긴다
    python3 ask.py --검색만 "연장근로 규칙 알려줘"   AI를 부르지 않고 검색 결과만 본다

두 방식 모두 대화 턴 수, 읽은 토큰, 걸린 시간을 함께 보여준다.
로그인된 claude CLI가 필요하다.
"""
import json
import subprocess
import sys
from pathlib import Path

색인파일 = Path("index.tsv")
조각폴더 = Path("chunks")
원본폴더 = Path("docs")

흔한말 = {"규칙", "규정", "알려줘", "뭐야", "어떻게", "얼마", "기준", "내용", "관련", "설명"}
뽑을조각수 = 3


def 클로드호출(프롬프트, 작업폴더, 도구):
    """claude CLI를 부르고 답변과 함께 사용량을 돌려준다."""
    결과 = subprocess.run(
        ["claude", "-p", 프롬프트, "--allowed-tools", 도구, "--output-format", "json"],
        cwd=작업폴더, capture_output=True, text=True,
    )
    응답 = json.loads(결과.stdout)
    사용량 = 응답.get("usage", {})
    읽은토큰 = (사용량.get("input_tokens", 0)
                + 사용량.get("cache_read_input_tokens", 0)
                + 사용량.get("cache_creation_input_tokens", 0))
    return {
        "답변": 응답.get("result", "").strip(),
        "턴": 응답.get("num_turns", 0),
        "읽은토큰": 읽은토큰,
        "초": 응답.get("duration_ms", 0) / 1000,
    }


def 사용량출력(사용량):
    print("  ── AI 호출 ──")
    print(f"  대화 턴     : {사용량['턴']}회")
    print(f"  읽은 토큰   : {사용량['읽은토큰']:,}")
    print(f"  걸린 시간   : {사용량['초']:.1f}초")
    print(f"\n[답변] {사용량['답변']}")


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


인자 = sys.argv[1:]
그냥모드 = "--그냥" in 인자
검색만 = "--검색만" in 인자
질문 = " ".join(a for a in 인자 if not a.startswith("--")) or "연장근로 규칙 알려줘"

print(f"[질문] {질문}\n")

# ── 방식 1. Claude Code에게 폴더째 맡긴다 ────────────────────────────
if 그냥모드:
    print("방식: Claude Code에게 그냥 묻는다  (우리가 만든 검색 코드를 쓰지 않는다)")
    print(f"  준 것       : {원본폴더}/ 폴더 통째로 ({len(list(원본폴더.glob('*.md')))}장)")
    print("  찾는 방법   : Claude Code가 알아서 (파일 열기·단어 검색)")
    사용량출력(클로드호출(질문, 원본폴더, "Read Grep Glob"))
    sys.exit()

# ── 방식 2. 색인으로 찾아서 조각만 넘긴다 ────────────────────────────
검색어, 히트 = 검색(질문)
print("방식: 색인으로 찾아서 조각만 넘긴다  (RAG)")
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

프롬프트 = (f"아래 근거로만 한국어로 답해줘. 근거에 없으면 없다고 말해줘.\n\n"
            f"[근거]\n{근거}\n\n[질문] {질문}")
사용량출력(클로드호출(프롬프트, ".", ""))

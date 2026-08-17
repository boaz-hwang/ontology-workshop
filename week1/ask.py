"""
ask.py — 질문을 숫자로 바꿔, 거리가 가까운 조각을 찾아 AI에게 준다.

    python3 ask.py "시간외근로수당 기준 알려줘"
    python3 ask.py --검색만 "…"      AI를 부르지 않고 거리 계산까지만 본다
    python3 ask.py --링크무시 "…"    조각 속 링크를 따라가지 않는다

질문도 embedding.py 와 같은 사전으로 숫자가 된다. 그래야 조각과 같은
좌표에서 거리를 잴 수 있다. 거리는 코사인 유사도로 재며 1에 가까울수록 가깝다.
AI 호출에는 로그인된 claude CLI 가 필요하다.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from embedding import 벡터만들기

색인파일 = Path("vectors.tsv")
조각폴더 = Path("chunks")

뽑을조각수 = 3
보여줄거리수 = 5

링크찾기 = re.compile(r"\]\((?P<문서>[^)#]+)#(?P<앵커>[^)]+)\)")


def 앵커(조항제목: str) -> str:
    """'제3조 (사전승인 원칙)' → '제3조-사전승인-원칙'  (link.py 와 같은 규칙)"""
    s = re.sub(r"[^\w\s-]", "", 조항제목.strip().lower())
    return re.sub(r"\s+", "-", s)


def 코사인(가: list, 나: list) -> float:
    """두 벡터 사이의 거리. 방향이 같을수록 1에 가깝다."""
    내적 = sum(a * b for a, b in zip(가, 나))
    크기 = math.sqrt(sum(a * a for a in 가)) * math.sqrt(sum(b * b for b in 나))
    return 내적 / 크기 if 크기 else 0.0


def 링크따라가기(조각파일들):
    """뽑힌 조각 안의 링크를 읽어, 가리키는 조각을 찾아온다. 한 단계만 따라간다."""
    따라간것 = []
    for 조각파일 in 조각파일들:
        본문 = (조각폴더 / 조각파일).read_text(encoding="utf-8")
        for m in 링크찾기.finditer(본문):
            찾은것 = 주소표.get((m.group("문서"), m.group("앵커")))
            if 찾은것 and 찾은것[0] not in 조각파일들 and 찾은것 not in 따라간것:
                따라간것.append(찾은것)
    return 따라간것


def 물어보기(근거, 질문):
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


if not 색인파일.is_file():
    sys.exit("vectors.tsv 가 없습니다. 먼저 python3 indexing.py 를 실행하세요.")

인자 = sys.argv[1:]
검색만 = "--검색만" in 인자
링크무시 = "--링크무시" in 인자
질문 = " ".join(a for a in 인자 if not a.startswith("--")) or "시간외근로수당 기준 알려줘"

줄들 = 색인파일.read_text(encoding="utf-8").splitlines()
축이름들 = 줄들[0].split("\t")[2:]
색인 = []
for 줄 in 줄들[1:]:
    칸들 = 줄.split("\t")
    색인.append((칸들[0], 칸들[1], [int(값) for 값 in 칸들[2:]]))

# 링크 주소 → 조각  (예: '03-연장근로.md#별표-1-연장근로-가산율' → '03-연장근로-10.md')
주소표 = {}
for 파일명, 제목, _ in 색인:
    원본문서 = 파일명.rsplit("-", 1)[0] + ".md"
    주소표[(원본문서, 앵커(제목))] = (파일명, 제목)

print(f"[질문] {질문}\n")

# ── 1. 질문도 숫자로 바꾼다 ─────────────────────────────────────
질문벡터표 = 벡터만들기(질문)
질문벡터 = [질문벡터표[축] for 축 in 축이름들]

print("① 질문을 숫자로 바꾼다 (embedding.py 와 같은 사전):")
for 축, 값 in 질문벡터표.items():
    if 값:
        print(f"     {축:<4} {값:>2}  {'█' * 값}")
print(f"     → 질문 벡터: {질문벡터}")

if not any(질문벡터):
    print("\n[답변] 질문의 어떤 말도 의미축 사전에 없어 벡터를 만들지 못했습니다.")
    print("       ← 임베딩은 사전(모델이 아는 말) 밖의 표현을 좌표로 만들지 못한다")
    sys.exit()

# ── 2. 색인의 모든 조각과 거리를 잰다 ───────────────────────────
# 거리가 같으면 표제어를 더 많이 말한 조각을 먼저 본다
점수표 = sorted(
    ((코사인(질문벡터, 벡터), sum(벡터), 파일명, 제목) for 파일명, 제목, 벡터 in 색인),
    reverse=True,
)
영점 = sum(1 for 점수, _, _, _ in 점수표 if 점수 == 0)

print(f"\n② 색인의 조각 {len(색인)}개와 거리를 잰다 (코사인 유사도 — 1에 가까울수록 가깝다):")
for 점수, _, 파일명, 제목 in 점수표[:보여줄거리수]:
    print(f"     {점수:.2f}  {파일명:<24} {제목}")
if 영점:
    print(f"     (유사도 0.00 조각 {영점}개 생략 — 겹치는 축 없음)")

# ── 3. 가까운 조각을 근거로 모아 AI에게 준다 ────────────────────
히트 = [(파일명, 제목) for 점수, _, 파일명, 제목 in 점수표[:뽑을조각수] if 점수 > 0]
쓸조각 = [파일명 for 파일명, _ in 히트]

print(f"\n③ 가장 가까운 조각 {len(쓸조각)}개를 근거로 모은다:")
for 파일명, 제목 in 히트:
    print(f"     {파일명:<24} {제목}")

따라간것 = [] if 링크무시 else 링크따라가기(쓸조각)
for 파일명, 제목 in 따라간것:
    print(f"     ↳ 링크  {파일명:<18} {제목}")
쓸조각 += [파일명 for 파일명, _ in 따라간것]

근거 = "\n\n".join((조각폴더 / f).read_text(encoding="utf-8") for f in 쓸조각)
딸린것 = f" + 링크 {len(따라간것)}" if 따라간것 else ""
print(f"\n  열어본 파일 : {1 + len(쓸조각)}개  (vectors.tsv 1 + 조각 {len(히트)}{딸린것})")
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

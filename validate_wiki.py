"""
validate_wiki.py — 위키가 규칙대로 만들어졌는지 검사한다.

    python3 validate_wiki.py            wiki/ 를 검사한다
    python3 validate_wiki.py 경로       다른 위키 폴더를 검사한다

Claude Code 가 pages/ 와 facts/ 를 만든 뒤에 실행한다.
사람 눈 대신 규칙 위반을 기계적으로 찾아 준다:
빠진 섹션, 깨진 출처 참조, 없는 페이지로 가는 링크, 잘못된 facts 스키마.
"""
import csv
import re
import sys
from pathlib import Path

필수폴더 = ["sources", "pages", "facts", "decisions", "templates"]
운영파일 = ["README.md", "CLAUDE.md", "templates/page.md", "templates/facts.csv"]
페이지섹션 = ["## 요약", "## 출처", "## 관련 페이지", "## 확인 필요"]
사실헤더 = ["subject", "relation", "object", "source", "status", "note"]
허용상태 = {"confirmed", "needs_review"}
출처찾기 = re.compile(r"sources/[A-Za-z0-9가-힣_.-]+(?:#[A-Za-z0-9가-힣_.-]+)?")

인자 = [a for a in sys.argv[1:] if not a.startswith("-")]
위키폴더 = Path(인자[0]).expanduser().resolve() if 인자 else Path(__file__).resolve().parent / "wiki"

문제들 = []


def 읽기(경로: Path) -> str:
    return 경로.read_text(encoding="utf-8")


def 페이지제목(경로: Path) -> str:
    for 줄 in 읽기(경로).splitlines():
        if 줄.startswith("# "):
            return 줄[2:].strip()
    return 경로.stem


def 섹션주소(제목: str) -> str:
    """'제3조 (연차휴가의 발생)' → '제3조-연차휴가의-발생'  (link.py 와 같은 규칙)"""
    s = re.sub(r"[^\w\s-]", "", 제목.strip().lower())
    return re.sub(r"\s+", "-", s)


def 출처확인(참조: str) -> str | None:
    파일명, _, 섹션 = 참조.partition("#")
    경로 = 위키폴더 / 파일명
    if not 경로.is_file():
        return f"출처 파일이 없습니다: {참조}"
    if 섹션:
        주소들 = {섹션주소(줄.lstrip("#").strip())
                  for 줄 in 읽기(경로).splitlines() if 줄.startswith("#")}
        if 섹션.lower() not in 주소들:
            return f"출처 섹션이 없습니다: {참조}"
    return None


if not 위키폴더.exists():
    sys.exit(f"위키 폴더가 없습니다: {위키폴더}\n먼저 python3 setup_wiki.py 를 실행하세요.")

# ── 1. 폴더 뼈대와 운영 파일 ────────────────────────────────────
for 이름 in 필수폴더:
    if not (위키폴더 / 이름).is_dir():
        문제들.append(f"폴더가 없습니다: {이름}/")

for 이름 in 운영파일:
    경로 = 위키폴더 / 이름
    if not 경로.is_file():
        문제들.append(f"파일이 없습니다: {이름}")
    elif not 읽기(경로).strip():
        문제들.append(f"빈 파일입니다: {이름}")

원본들 = sorted((위키폴더 / "sources").glob("*.md")) if (위키폴더 / "sources").is_dir() else []
if len(원본들) < 3:
    문제들.append("sources/ 에 원본 문서가 3편 이상 있어야 합니다")

# ── 2. 페이지: 섹션·출처·위키 링크 ──────────────────────────────
페이지들 = sorted((위키폴더 / "pages").glob("*.md")) if (위키폴더 / "pages").is_dir() else []
if len(페이지들) < 3:
    문제들.append("pages/ 에 개념 페이지가 3개 이상 있어야 합니다")

제목들 = {페이지제목(경로) for 경로 in 페이지들}
for 경로 in 페이지들:
    본문 = 읽기(경로)
    이름 = 경로.relative_to(위키폴더)
    for 섹션 in 페이지섹션:
        if 섹션 not in 본문:
            문제들.append(f"{이름} 에 {섹션} 섹션이 없습니다")
    if "sources/" not in 본문:
        문제들.append(f"{이름} 에 출처 참조가 없습니다")
    for 참조 in 출처찾기.findall(본문):
        오류 = 출처확인(참조)
        if 오류:
            문제들.append(f"{이름} {오류}")
    for 링크 in re.findall(r"\[\[([^\]]+)\]\]", 본문):
        if 링크 not in 제목들:
            문제들.append(f"{이름} 가 없는 페이지 [[{링크}]] 로 링크합니다")

# ── 3. facts: 스키마·status·출처 ────────────────────────────────
사실파일 = 위키폴더 / "facts" / "candidates.csv"
if not 사실파일.is_file():
    문제들.append("facts/candidates.csv 가 없습니다")
else:
    with 사실파일.open(newline="", encoding="utf-8") as f:
        행들 = list(csv.DictReader(f))
    if not 행들:
        문제들.append("facts/candidates.csv 에 데이터 행이 없습니다")
    if 행들 and list(행들[0].keys()) != 사실헤더:
        문제들.append(f"facts/candidates.csv 헤더는 {','.join(사실헤더)} 여야 합니다")
    for 번호, 행 in enumerate(행들, start=2):
        if 행.get("status") not in 허용상태:
            문제들.append(f"facts/candidates.csv {번호}행: status 가 잘못되었습니다: {행.get('status')!r}")
        if not 행.get("source", "").startswith("sources/"):
            문제들.append(f"facts/candidates.csv {번호}행: source 는 sources/ 로 시작해야 합니다")
        else:
            오류 = 출처확인(행["source"])
            if 오류:
                문제들.append(f"facts/candidates.csv {번호}행: {오류}")

# ── 4. 보류 항목 ────────────────────────────────────────────────
질문파일 = 위키폴더 / "decisions" / "open-questions.md"
if not 질문파일.is_file():
    문제들.append("decisions/open-questions.md 가 없습니다")
elif not [줄 for 줄 in 읽기(질문파일).splitlines() if 줄.lstrip().startswith("- ")]:
    문제들.append("decisions/open-questions.md 에 검토 항목이 1개 이상 있어야 합니다")

# ── 5. 결과 ─────────────────────────────────────────────────────
if 문제들:
    print(f"위키 검증 실패: 문제 {len(문제들)}개")
    for 문제 in 문제들:
        print(f"- {문제}")
    sys.exit(1)

print(f"위키 검증 통과: {위키폴더}")

"""
setup_wiki.py — 실습용 위키 폴더(wiki/)를 만든다.

    python3 setup_wiki.py            처음 만들 때
    python3 setup_wiki.py --force    기존 파일을 덮어쓰고 다시 만들 때

week1/docs/ 의 규정 문서 전부를 wiki/sources/ 로 복사하고,
pages/ facts/ decisions/ templates/ 폴더와 기본 파일을 만든다.
git 저장소도 만들어 씨앗 커밋을 남긴다. 이후 Claude Code 가 만든
변경은 wiki/ 안에서 git diff 로 확인할 수 있다.

CLAUDE.md 는 일부러 만들지 않는다.
위키 규칙을 직접 붙여 넣는 것이 실습의 첫 단계이기 때문이다.

완전히 처음부터 다시 시작하려면 wiki/ 를 지우고 재실행한다.
"""
import shutil
import subprocess
import sys
from pathlib import Path

기준폴더 = Path(__file__).resolve().parent
원본폴더 = 기준폴더 / "week1" / "docs"
위키폴더 = 기준폴더 / "wiki"
강제 = "--force" in sys.argv

하위폴더들 = ["sources", "pages", "facts", "decisions", "templates"]


def 쓰기(경로: Path, 내용: str) -> None:
    if 경로.exists() and 경로.read_text(encoding="utf-8").strip() and not 강제:
        sys.exit(f"이미 내용이 있는 파일은 덮어쓰지 않습니다: {경로}\n"
                 f"다시 만들려면 --force 를 붙이세요.")
    경로.parent.mkdir(parents=True, exist_ok=True)
    경로.write_text(내용, encoding="utf-8")


README = """# HR 규정 LLM Wiki

이 폴더는 파일 기반 LLM Wiki 실습 공간입니다.

- 원본 규정 문서는 sources/ 에 둡니다. 수정하지 않습니다.
- 사람이 읽는 개념 페이지는 pages/ 에 만듭니다.
- 기계가 읽는 사실 후보는 facts/ 에 기록합니다.
- 사람이 판단할 보류 항목은 decisions/open-questions.md 에 모읍니다.
- 페이지 형식은 templates/ 를 따릅니다.

시작하기 전에 CLAUDE.md 를 직접 만들어 위키 규칙을 붙여 넣으세요.
"""

페이지틀 = """# 개념 이름

## 요약
- 이 개념을 3문장 이내로 설명합니다.

## 출처
- sources/...#섹션-이름

## 관련 페이지
- [[관련 개념]]

## 확인 필요
- 출처가 부족하거나 관계가 애매한 항목을 적습니다.
"""

사실틀 = "subject,relation,object,source,status,note\n"

열린질문 = """# Open Questions

## 중복 개념 후보

## 모호한 관계명

## 출처 부족

## 기존 내용과 충돌할 수 있는 항목
"""


# ── 1. 폴더 뼈대 ────────────────────────────────────────────────
위키폴더.mkdir(exist_ok=True)
for 이름 in 하위폴더들:
    (위키폴더 / 이름).mkdir(exist_ok=True)

# ── 2. 규정 문서를 sources/ 로 복사 ─────────────────────────────
문서들 = sorted(원본폴더.glob("*.md"))
if not 문서들:
    sys.exit(f"원본 문서가 없습니다: {원본폴더}")
for 문서 in 문서들:
    대상 = 위키폴더 / "sources" / 문서.name
    if 대상.exists() and 대상.read_text(encoding="utf-8").strip() and not 강제:
        sys.exit(f"이미 내용이 있는 파일은 덮어쓰지 않습니다: {대상}\n"
                 f"다시 만들려면 --force 를 붙이세요.")
    shutil.copy2(문서, 대상)

# ── 3. 기본 파일 ────────────────────────────────────────────────
쓰기(위키폴더 / "README.md", README)
쓰기(위키폴더 / "templates" / "page.md", 페이지틀)
쓰기(위키폴더 / "templates" / "facts.csv", 사실틀)
쓰기(위키폴더 / "decisions" / "open-questions.md", 열린질문)

# ── 4. git 저장소와 씨앗 커밋 ───────────────────────────────────
git = shutil.which("git")
if git and not (위키폴더 / ".git").exists():
    subprocess.run([git, "-C", str(위키폴더), "init"],
                   check=False, capture_output=True, text=True)
if git and (위키폴더 / ".git").exists():
    커밋있음 = subprocess.run(
        [git, "-C", str(위키폴더), "rev-parse", "--verify", "HEAD"],
        check=False, capture_output=True, text=True,
    ).returncode == 0
    if not 커밋있음:
        subprocess.run([git, "-C", str(위키폴더), "add", "."],
                       check=False, capture_output=True, text=True)
        subprocess.run(
            [git, "-C", str(위키폴더),
             "-c", "user.name=위키 실습", "-c", "user.email=wiki@example.invalid",
             "commit", "-m", "위키 실습 시작 상태"],
            check=False, capture_output=True, text=True,
        )

print(f"wiki/ 를 만들었습니다. ({위키폴더})")
print(f"  sources/   규정 문서 {len(문서들)}개 (week1/docs 에서 복사)")
print("  pages/     비어 있음 — Claude Code 가 채울 공간")
print("  facts/     비어 있음 — templates/facts.csv 스키마를 따른다")
print("  decisions/ open-questions.md 뼈대")
print("  templates/ page.md, facts.csv")
print()
print("다음 단계:")
print("  1. wiki/CLAUDE.md 를 직접 만들어 위키 규칙을 붙여 넣으세요.")
print("  2. cd wiki 후 claude 를 실행해 pages/ 생성을 요청하세요.")
print("  3. 결과는 git -C wiki status 와 git -C wiki diff 로 확인합니다.")
print("  4. python3 validate_wiki.py 로 위키가 규칙을 지켰는지 검사합니다.")

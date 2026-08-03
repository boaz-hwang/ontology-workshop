"""
split.py — 규정 문서를 조항 단위 '조각'으로 나눈다.

    python3 split.py

docs/ 안의 문서를 읽어 빈 줄을 기준으로 자르고, chunks/ 에 조각 파일로 저장한다.
이 규정 문서들은 조항 하나가 빈 줄로 구분되어 있어서, 조각 하나 = 조항 하나가 된다.
"""
from pathlib import Path

원본폴더 = Path("docs")
조각폴더 = Path("chunks")

# 조각 폴더를 비우고 새로 만든다
조각폴더.mkdir(exist_ok=True)
for 기존조각 in 조각폴더.glob("*.md"):
    기존조각.unlink()

전체조각수 = 0
원본목록 = sorted(원본폴더.glob("*.md"))

for 문서 in 원본목록:
    내용 = 문서.read_text(encoding="utf-8")

    # 빈 줄을 기준으로 자른다
    덩어리들 = [덩어리.strip() for 덩어리 in 내용.split("\n\n") if 덩어리.strip()]

    # 첫 덩어리는 문서 제목이다. 조각마다 제목을 붙여 어느 규정인지 알 수 있게 한다.
    제목 = 덩어리들[0]
    조항들 = 덩어리들[1:]

    for 번호, 조항 in enumerate(조항들, start=1):
        조각 = f"{제목}\n\n{조항}\n"
        (조각폴더 / f"{문서.stem}-{번호:02d}.md").write_text(조각, encoding="utf-8")

    print(f"{문서.name:<26} → 조각 {len(조항들):>2}개")
    전체조각수 += len(조항들)

print()
print(f"원본 {len(원본목록)}장  →  조각 {전체조각수}개   ({조각폴더}/ 에 저장했습니다)")

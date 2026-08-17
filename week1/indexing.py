"""
indexing.py — 흩어진 벡터를 색인 한 장으로 모은다.

    python3 indexing.py

embedding.py 가 만든 vectors/ 의 벡터들을 vectors.tsv 한 장으로 모은다.
검색할 때 파일 105개를 하나씩 여는 대신 이 한 장만 읽으면 된다. 그것이 색인이다.
사람이 결과를 읽을 수 있게 조각의 조항 제목도 함께 붙인다.
"""
import sys
from pathlib import Path

조각폴더 = Path("chunks")
벡터폴더 = Path("vectors")
색인파일 = Path("vectors.tsv")


def 조항제목(본문: str) -> str:
    for 줄 in 본문.splitlines():
        if 줄.startswith("## "):
            return 줄[3:].strip()
    return 본문.splitlines()[0].strip()


벡터파일들 = sorted(벡터폴더.glob("*.tsv"))
if not 벡터파일들:
    sys.exit("vectors/ 가 비어 있습니다. 먼저 python3 embedding.py 를 실행하세요.")

축이름들 = None
줄들 = []
for 벡터파일 in 벡터파일들:
    쌍들 = [줄.split("\t") for 줄 in 벡터파일.read_text(encoding="utf-8").splitlines()]
    if 축이름들 is None:
        축이름들 = [축 for 축, _ in 쌍들]
    조각이름 = 벡터파일.stem + ".md"
    제목 = 조항제목((조각폴더 / 조각이름).read_text(encoding="utf-8"))
    줄들.append(f"{조각이름}\t{제목}\t" + "\t".join(값 for _, 값 in 쌍들))

머리줄 = "조각\t제목\t" + "\t".join(축이름들)
색인파일.write_text(머리줄 + "\n" + "\n".join(줄들) + "\n", encoding="utf-8")

print(f"흩어진 벡터 {len(줄들)}장 → 색인 1장 ({색인파일}, {색인파일.stat().st_size:,}바이트)")
print()
print("색인 미리보기 (앞 3줄):")
print(f"  {'조각':<24} {'제목':<20} {' '.join(축이름들)}")
for 줄 in 줄들[:3]:
    칸들 = 줄.split("\t")
    print(f"  {칸들[0]:<24} {칸들[1]:<20} {'  '.join(칸들[2:])}")

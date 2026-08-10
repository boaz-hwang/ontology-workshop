# Obsidian 스타터

새로 만든 Obsidian 계정/볼트에서 **명령 한 줄**로 워크샵 기준 환경(플러그인 10개 · 테마 3종 · 단축키 · 스니펫 · 각종 설정)을 그대로 적용하는 패키지입니다.

플러그인 본체(`main.js`)까지 함께 담겨 있어 **인터넷 연결이나 커뮤니티 플러그인 스토어 없이도** 동일한 버전이 설치됩니다.

---

## 빠른 시작

### macOS / Linux

```bash
cd "Obsidian 스타터"
chmod +x install.sh
./install.sh ~/MyVault
```

경로를 생략하면 물어봅니다.

```bash
./install.sh
```

### Windows (PowerShell)

```powershell
cd "Obsidian 스타터"
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Vault C:\MyVault
```

### 옵션

| 옵션 | 설명 |
|---|---|
| `-y` / `--yes` (`-Yes`) | 확인 질문 없이 진행 |
| `-n` / `--dry-run` (`-DryRun`) | 무엇이 복사될지만 출력, 실제 변경 없음 |
| `-h` / `--help` | 사용법 |

설치 후 Obsidian 에서 해당 폴더를 **Open folder as vault** 로 열고, 커뮤니티 플러그인 신뢰 확인 창에서 **Trust author and enable plugins** 를 누르면 끝입니다.

---

## 무엇이 설치되나

### 커뮤니티 플러그인 (10개)

| 플러그인 | ID | 버전 |
|---|---|---|
| Tasks | `obsidian-tasks-plugin` | 8.3.0 |
| Calendar | `calendar` | 1.5.10 |
| Dataview | `dataview` | 0.5.68 |
| Style Settings | `obsidian-style-settings` | 1.0.9 |
| Templater | `templater-obsidian` | 2.24.3 |
| Periodic Notes | `periodic-notes` | 0.0.17 |
| Callout Manager | `callout-manager` | 1.1.1 |
| Tracker | `obsidian-tracker` | 1.19.0 |
| Contribution Graph | `contribution-graph` | 0.10.0 |
| Go to Line | `obsidian-go-to-line` | 0.0.2 |

플러그인별 설정값(`data.json`)도 함께 복사되므로, 상태 기호·전역 필터·주기 노트 폴더 같은 세부 설정까지 동일해집니다.

### 테마 (3종)

`AnuPpuccin` 1.5.0 (기본 적용) · `Minimal` 7.7.3 · `Atom`

### CSS 스니펫

`color-extend.css` (활성) · `tweets-callout.css`

### 코어 플러그인 / 설정

- 코어 플러그인 on/off 상태 (`core-plugins.json`) — Daily notes, Templates, Slides, Bases 등
- 단축키 20여 개 (`hotkeys.json`) — `Ctrl+T` 오늘 노트, `Cmd+L/R` 사이드바, `Ctrl+G` 줄 이동 등
- 외형 (`appearance.json`) — 라이트 테마, 액센트 `#2a347e`
- 에디터/PDF 내보내기 (`app.json`), 그래프 뷰, 속성 타입, 데일리 노트, 템플릿 폴더 설정

### 볼트 시드 (`vault-seed/`)

설정이 참조하는 폴더/파일이 없으면 만들어 줍니다. **이미 있으면 건너뜁니다.**

- `Daily/` — 데일리 노트 저장 폴더
- `Templates/Daily notes.md` · `TOC.md` · `weekly.md`
- `Templates/user_functions/` — Templater User Scripts 폴더

---

## 폴더 구조

```
Obsidian 스타터/
├── README.md
├── install.sh          # macOS / Linux
├── install.ps1         # Windows
├── config/             # → 볼트의 .obsidian/ 로 복사됨
│   ├── *.json          # 설정 11개
│   ├── plugins/        # 플러그인 10개 (본체 + data.json)
│   ├── themes/         # 테마 3종
│   └── snippets/       # CSS 스니펫 2개
└── vault-seed/         # → 볼트 루트로 복사 (없을 때만)
    ├── Daily/
    └── Templates/
```

---

## 원본에서 의도적으로 제외한 것

| 항목 | 이유 |
|---|---|
| `workspace.json` | 열린 탭·창 배치 등 개인 작업 상태. 새 볼트에서는 Obsidian 이 알아서 만듭니다. |
| `core-plugins-migration.json` | 구버전 마이그레이션 잔재. |
| `Templates/scripts/` | 구글 캘린더 연동 스크립트 + `credentials.json` 자격증명 포함. |
| `Templates/user_functions/*.js` | 위 스크립트에 의존. 대신 작성 가이드를 넣어 뒀습니다. |
| `appearance.json` 의 `my-style` 스니펫 | 원본에 파일이 없는 죽은 참조. |
| 실제 노트 | 설정 패키지이므로 본문 노트는 담지 않습니다. |

`Templates/Daily notes.md` 는 개인 습관 항목과 캘린더 연동 호출을 일반 문구로 바꾼 버전입니다.
**설정 파일 자체는 원본과 동일합니다.**

---

## 되돌리기

기존 `.obsidian` 이 있으면 설치 전에 `.obsidian.backup.<날짜-시각>` 으로 자동 백업됩니다.

```bash
rm -rf ~/MyVault/.obsidian
mv ~/MyVault/.obsidian.backup.20260811-101500 ~/MyVault/.obsidian
```

---

## 문제 해결

**플러그인이 하나도 안 보여요**
설정 → 커뮤니티 플러그인 → **제한 모드(Restricted mode)** 를 끄고 Obsidian 을 재시작하세요.

**설치했는데 설정이 원래대로 돌아왔어요**
Obsidian 이 켜진 상태로 설치하면 종료 시 기존 설정을 다시 씁니다. Obsidian 을 완전히 종료한 뒤 다시 실행하세요.

**Windows 에서 스크립트 실행이 차단돼요**
`powershell -ExecutionPolicy Bypass -File .\install.ps1` 로 실행하세요.

**테마가 안 바뀌어요**
설정 → 모양 → 테마에서 `AnuPpuccin` 을 직접 선택하세요.

---

기준 환경: Obsidian 1.13.x (macOS). 플러그인·테마는 각 제작자의 라이선스를 따르며, 워크샵 실습 편의를 위해 그대로 포함했습니다.

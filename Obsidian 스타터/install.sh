#!/usr/bin/env bash
#
# Obsidian 스타터 설치 스크립트 (macOS / Linux)
#
#   ./install.sh                  # 볼트 경로를 물어봄
#   ./install.sh ~/MyVault        # 경로 지정
#   ./install.sh ~/MyVault --yes  # 확인 없이 진행
#   ./install.sh ~/MyVault --dry-run
#
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SRC="$SCRIPT_DIR/config"
SEED_SRC="$SCRIPT_DIR/vault-seed"

BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'
info()  { printf '%s\n' "$*"; }
ok()    { printf '%s✓%s %s\n' "$GREEN" "$RESET" "$*"; }
warn()  { printf '%s!%s %s\n' "$YELLOW" "$RESET" "$*"; }
die()   { printf '%s✗ %s%s\n' "$RED" "$*" "$RESET" >&2; exit 1; }

VAULT=""
ASSUME_YES=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    -y|--yes)     ASSUME_YES=1 ;;
    -n|--dry-run) DRY_RUN=1 ;;
    -h|--help)    sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)           die "알 수 없는 옵션: $arg" ;;
    *)            VAULT="$arg" ;;
  esac
done

[[ -d "$CONFIG_SRC" ]] || die "config/ 폴더를 찾을 수 없습니다: $CONFIG_SRC"

printf '%s\n' "${BOLD}Obsidian 스타터${RESET} — 플러그인·테마·설정 일괄 적용"
echo

# ── 1. 볼트 경로 확인 ────────────────────────────────────────────────────────
if [[ -z "$VAULT" ]]; then
  read -r -p "Obsidian 볼트 경로를 입력하세요 (없으면 새로 만듭니다): " VAULT
  [[ -n "$VAULT" ]] || die "경로가 비어 있습니다."
fi
VAULT="${VAULT/#\~/$HOME}"

if [[ ! -d "$VAULT" ]]; then
  if [[ $ASSUME_YES -eq 0 ]]; then
    read -r -p "폴더가 없습니다. '$VAULT' 를 새로 만들까요? [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]] || die "취소했습니다."
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    info "${DIM}  [dry-run] 볼트 폴더 생성: $VAULT${RESET}"
  else
    mkdir -p "$VAULT"
    ok "볼트 폴더 생성: $VAULT"
  fi
fi
# dry-run 에서는 폴더가 아직 없을 수 있으므로 존재할 때만 절대경로로 정규화한다.
[[ -d "$VAULT" ]] && VAULT="$(cd -- "$VAULT" && pwd)"
OBS="$VAULT/.obsidian"

# ── 2. Obsidian 실행 중이면 경고 ─────────────────────────────────────────────
if pgrep -x "Obsidian" >/dev/null 2>&1 || pgrep -x "obsidian" >/dev/null 2>&1; then
  warn "Obsidian 이 실행 중입니다. 종료하지 않으면 설정이 되돌려질 수 있습니다."
  if [[ $ASSUME_YES -eq 0 ]]; then
    read -r -p "그래도 계속할까요? [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]] || die "Obsidian 을 종료한 뒤 다시 실행해 주세요."
  fi
fi

# ── 3. 기존 설정 백업 ────────────────────────────────────────────────────────
if [[ -d "$OBS" ]]; then
  BACKUP="$OBS.backup.$(date +%Y%m%d-%H%M%S)"
  warn "기존 설정이 있습니다 → $BACKUP 로 백업합니다."
  if [[ $ASSUME_YES -eq 0 ]]; then
    read -r -p "계속할까요? [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]] || die "취소했습니다."
  fi
  [[ $DRY_RUN -eq 1 ]] || cp -R "$OBS" "$BACKUP"
  ok "백업 완료"
fi

# ── 4. 설정 복사 ─────────────────────────────────────────────────────────────
copy() { # copy <src> <dst>
  if [[ $DRY_RUN -eq 1 ]]; then
    printf '%s  [dry-run] %s → %s%s\n' "$DIM" "$1" "$2" "$RESET"
  else
    mkdir -p "$(dirname -- "$2")"
    cp -R "$1" "$2"
  fi
}

[[ $DRY_RUN -eq 1 ]] || mkdir -p "$OBS"
shopt -s dotglob
for item in "$CONFIG_SRC"/*; do
  name="$(basename -- "$item")"
  [[ "$name" == ".DS_Store" ]] && continue
  [[ $DRY_RUN -eq 1 ]] || rm -rf "$OBS/$name"
  copy "$item" "$OBS/$name"
done
shopt -u dotglob
ok "설정·플러그인·테마·스니펫 복사 완료 → $OBS"

# ── 5. 볼트 시드 (없을 때만) ─────────────────────────────────────────────────
if [[ -d "$SEED_SRC" ]]; then
  for item in "$SEED_SRC"/*; do
    name="$(basename -- "$item")"
    if [[ -e "$VAULT/$name" ]]; then
      info "  ${DIM}건너뜀 (이미 있음): $name${RESET}"
    else
      copy "$item" "$VAULT/$name"
      ok "시드 생성: $name/"
    fi
  done
  [[ $DRY_RUN -eq 1 ]] || rm -f "$VAULT/Daily/.gitkeep"
fi

# ── 6. 검증 ──────────────────────────────────────────────────────────────────
echo
if [[ $DRY_RUN -eq 1 ]]; then
  info "${DIM}dry-run 이므로 아무것도 바꾸지 않았습니다.${RESET}"
  exit 0
fi

expected_plugins=$(python3 -c "import json;print(len(json.load(open('$CONFIG_SRC/community-plugins.json'))))" 2>/dev/null || echo "?")
actual_plugins=$(find "$OBS/plugins" -maxdepth 2 -name manifest.json 2>/dev/null | wc -l | tr -d ' ')
actual_themes=$(find "$OBS/themes" -maxdepth 2 -name manifest.json 2>/dev/null | wc -l | tr -d ' ')
printf '%s설치 결과%s  커뮤니티 플러그인 %s/%s · 테마 %s개\n' "$BOLD" "$RESET" "$actual_plugins" "$expected_plugins" "$actual_themes"

cat <<EOF

${BOLD}다음 단계${RESET}
  1. Obsidian 을 열고 ${BOLD}Open folder as vault${RESET} 로 아래 폴더를 선택하세요.
       $VAULT
  2. 커뮤니티 플러그인 실행 여부를 묻는 창이 뜨면 ${BOLD}Trust author and enable plugins${RESET} 를 누릅니다.
     (설정 → 커뮤니티 플러그인 → 제한 모드 끄기)
  3. 설정 → 모양 에서 테마가 ${BOLD}AnuPpuccin${RESET} 인지 확인합니다.

문제가 생기면 백업 폴더(.obsidian.backup.*)로 되돌릴 수 있습니다.
EOF

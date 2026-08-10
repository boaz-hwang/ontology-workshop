<#
Obsidian 스타터 설치 스크립트 (Windows / PowerShell)

  .\install.ps1                        # 볼트 경로를 물어봄
  .\install.ps1 -Vault C:\MyVault      # 경로 지정
  .\install.ps1 -Vault C:\MyVault -Yes # 확인 없이 진행
  .\install.ps1 -Vault C:\MyVault -DryRun

실행 정책 때문에 막히면:
  powershell -ExecutionPolicy Bypass -File .\install.ps1
#>
[CmdletBinding()]
param(
    [string]$Vault,
    [switch]$Yes,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigSrc = Join-Path $ScriptDir 'config'
$SeedSrc   = Join-Path $ScriptDir 'vault-seed'

function Write-Ok   ($m) { Write-Host "[OK] $m"   -ForegroundColor Green }
function Write-Warn ($m) { Write-Host "[!] $m"    -ForegroundColor Yellow }
function Stop-Fail  ($m) { Write-Host "[X] $m"    -ForegroundColor Red; exit 1 }

function Confirm-Step ($message) {
    if ($Yes) { return $true }
    $reply = Read-Host "$message [y/N]"
    return $reply -match '^[Yy]$'
}

if (-not (Test-Path $ConfigSrc)) { Stop-Fail "config 폴더를 찾을 수 없습니다: $ConfigSrc" }

Write-Host "Obsidian 스타터 - 플러그인/테마/설정 일괄 적용" -ForegroundColor Cyan
Write-Host ""

# 1. 볼트 경로
if (-not $Vault) {
    $Vault = Read-Host "Obsidian 볼트 경로를 입력하세요 (없으면 새로 만듭니다)"
    if (-not $Vault) { Stop-Fail "경로가 비어 있습니다." }
}

if (-not (Test-Path $Vault)) {
    if (-not (Confirm-Step "폴더가 없습니다. '$Vault' 를 새로 만들까요?")) { Stop-Fail "취소했습니다." }
    if (-not $DryRun) { New-Item -ItemType Directory -Path $Vault -Force | Out-Null }
    Write-Ok "볼트 폴더 생성: $Vault"
}
if (-not $DryRun) { $Vault = (Resolve-Path $Vault).Path }
$Obs = Join-Path $Vault '.obsidian'

# 2. Obsidian 실행 중 확인
if (Get-Process -Name 'Obsidian' -ErrorAction SilentlyContinue) {
    Write-Warn "Obsidian 이 실행 중입니다. 종료하지 않으면 설정이 되돌려질 수 있습니다."
    if (-not (Confirm-Step "그래도 계속할까요?")) { Stop-Fail "Obsidian 을 종료한 뒤 다시 실행해 주세요." }
}

# 3. 기존 설정 백업
if (Test-Path $Obs) {
    $stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backup = "$Obs.backup.$stamp"
    Write-Warn "기존 설정이 있습니다 -> $backup 로 백업합니다."
    if (-not (Confirm-Step "계속할까요?")) { Stop-Fail "취소했습니다." }
    if (-not $DryRun) { Copy-Item $Obs $backup -Recurse -Force }
    Write-Ok "백업 완료"
}

# 4. 설정 복사
if (-not $DryRun) { New-Item -ItemType Directory -Path $Obs -Force | Out-Null }
Get-ChildItem -Path $ConfigSrc -Force | Where-Object { $_.Name -ne '.DS_Store' } | ForEach-Object {
    $dest = Join-Path $Obs $_.Name
    if ($DryRun) {
        Write-Host "  [dry-run] $($_.FullName) -> $dest" -ForegroundColor DarkGray
    } else {
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
        Copy-Item $_.FullName $dest -Recurse -Force
    }
}
Write-Ok "설정/플러그인/테마/스니펫 복사 완료 -> $Obs"

# 5. 볼트 시드 (없을 때만)
if (Test-Path $SeedSrc) {
    Get-ChildItem -Path $SeedSrc -Force | ForEach-Object {
        $dest = Join-Path $Vault $_.Name
        if (Test-Path $dest) {
            Write-Host "  건너뜀 (이미 있음): $($_.Name)" -ForegroundColor DarkGray
        } elseif ($DryRun) {
            Write-Host "  [dry-run] $($_.FullName) -> $dest" -ForegroundColor DarkGray
        } else {
            Copy-Item $_.FullName $dest -Recurse -Force
            Write-Ok "시드 생성: $($_.Name)"
        }
    }
    $keep = Join-Path $Vault 'Daily\.gitkeep'
    if ((-not $DryRun) -and (Test-Path $keep)) { Remove-Item $keep -Force }
}

Write-Host ""
if ($DryRun) {
    Write-Host "dry-run 이므로 아무것도 바꾸지 않았습니다." -ForegroundColor DarkGray
    exit 0
}

# 6. 검증
$expected = (Get-Content (Join-Path $ConfigSrc 'community-plugins.json') -Raw | ConvertFrom-Json).Count
$actualPlugins = (Get-ChildItem (Join-Path $Obs 'plugins') -Recurse -Filter 'manifest.json' -ErrorAction SilentlyContinue).Count
$actualThemes  = (Get-ChildItem (Join-Path $Obs 'themes')  -Recurse -Filter 'manifest.json' -ErrorAction SilentlyContinue).Count
Write-Host "설치 결과: 커뮤니티 플러그인 $actualPlugins/$expected, 테마 $actualThemes 개" -ForegroundColor Cyan

@"

다음 단계
  1. Obsidian 을 열고 'Open folder as vault' 로 아래 폴더를 선택하세요.
       $Vault
  2. 커뮤니티 플러그인 실행 여부를 묻는 창이 뜨면 'Trust author and enable plugins' 를 누릅니다.
     (설정 -> 커뮤니티 플러그인 -> 제한 모드 끄기)
  3. 설정 -> 모양 에서 테마가 AnuPpuccin 인지 확인합니다.

문제가 생기면 백업 폴더(.obsidian.backup.*)로 되돌릴 수 있습니다.
"@ | Write-Host

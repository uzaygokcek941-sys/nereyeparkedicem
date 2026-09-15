# wv/ yayin paketini derler ve imzalar.
#
# Parolayi BU DOSYA TUTMAZ: jarsigner calisma aninda sorar, sen yazarsin.
# Parolayi komut satirina da yazma (-storepass) - PowerShell gecmisine dusuyor.
#
# Kullanim:
#   .\imzala.ps1 -Keystore "C:\yol\yayin.keystore" -Alias yayin
param(
    [Parameter(Mandatory = $true)][string]$Keystore,
    [Parameter(Mandatory = $true)][string]$Alias,
    [string]$JavaHome = "C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot",
    [string]$AndroidHome = "D:\dev\android-sdk"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

if (-not (Test-Path $Keystore)) {
    Write-Error ("Keystore bulunamadi: $Keystore`nOnce uret:`n" +
        "  keytool -genkeypair -v -keystore yayin.keystore -alias $Alias -keyalg RSA -keysize 2048 -validity 10000")
}

$env:JAVA_HOME = $JavaHome
$env:ANDROID_HOME = $AndroidHome
$aab = "app\build\outputs\bundle\release\app-release.aab"

Write-Host "[1/3] bundleRelease derleniyor..." -ForegroundColor Cyan
& .\gradlew.bat bundleRelease --no-daemon
if ($LASTEXITCODE -ne 0) { Write-Error "Derleme basarisiz (exit $LASTEXITCODE)" }
if (-not (Test-Path $aab)) { Write-Error "AAB uretilmedi: $aab" }

Write-Host "[2/3] imzalaniyor (parolayi jarsigner soracak)..." -ForegroundColor Cyan
& "$JavaHome\bin\jarsigner.exe" -verbose:summary -sigalg SHA256withRSA -digestalg SHA-256 `
    -keystore $Keystore $aab $Alias
if ($LASTEXITCODE -ne 0) { Write-Error "Imzalama basarisiz (exit $LASTEXITCODE)" }

Write-Host "[3/3] imza dogrulaniyor..." -ForegroundColor Cyan
& "$JavaHome\bin\jarsigner.exe" -verify $aab
if ($LASTEXITCODE -ne 0) { Write-Error "Dogrulama basarisiz" }

$boyut = (Get-Item $aab).Length
Write-Host "`nHAZIR: $aab  ($('{0:N0}' -f $boyut) bayt, imzali)" -ForegroundColor Green
Write-Host "Play Console -> Kapali test -> Yeni surum -> bu dosyayi yukle."

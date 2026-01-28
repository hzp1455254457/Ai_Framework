# GTK+ 运行时库安装脚本
# 用于 WeasyPrint PDF 生成功能

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GTK+ 运行时库安装指南" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装
$gtkPaths = @(
    "C:\Program Files\GTK3-Runtime Win64\bin",
    "C:\GTK3-Runtime Win64\bin",
    "$env:ProgramFiles\GTK3-Runtime Win64\bin"
)

$installed = $false
foreach ($path in $gtkPaths) {
    if (Test-Path $path) {
        Write-Host "✓ 找到 GTK+ 安装: $path" -ForegroundColor Green
        $installed = $true
        break
    }
}

if (-not $installed) {
    Write-Host "✗ 未找到 GTK+ 安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "请按照以下步骤安装 GTK+ 运行时库：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Method 1: Use winget (Recommended)" -ForegroundColor Cyan
    Write-Host "  winget install --id tschoonj.GTKForWindows" -ForegroundColor White
    Write-Host ""
    Write-Host "Method 2: Manual download and install" -ForegroundColor Cyan
    Write-Host "  1. 访问: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases" -ForegroundColor White
    Write-Host "  2. 下载最新的 'GTK3-Runtime Win64' 安装程序" -ForegroundColor White
    Write-Host "  3. 运行安装程序完成安装" -ForegroundColor White
    Write-Host "  4. 安装完成后重启服务器" -ForegroundColor White
    Write-Host ""
    Write-Host "安装完成后，请运行此脚本验证安装。" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "验证 WeasyPrint..." -ForegroundColor Cyan
    python -c "try:
    from weasyprint import HTML
    print('✓ WeasyPrint 可用，PDF 生成功能正常')
except Exception as e:
    print(f'✗ WeasyPrint 不可用: {e}')"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

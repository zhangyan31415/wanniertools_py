# Windows DLL依赖检查脚本
# 专门用于诊断wannier-tools的DLL问题

param(
    [string]$TargetExe = "wt-py.exe",
    [switch]$Detailed,
    [switch]$SaveReport
)

Write-Host "=== Windows DLL依赖检查工具 ===" -ForegroundColor Cyan
Write-Host "目标程序: $TargetExe" -ForegroundColor Yellow

# 1. 检查目标程序是否存在
if (-not (Test-Path $TargetExe)) {
    Write-Host "❌ 错误: 找不到 $TargetExe" -ForegroundColor Red
    Write-Host "请确保在包含 wt-py.exe 的目录中运行此脚本" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ 找到目标程序: $TargetExe" -ForegroundColor Green

# 2. 检查PATH中的关键DLL
$CriticalDLLs = @(
    "msvcrt.dll",
    "msvcp140.dll", 
    "vcruntime140.dll",
    "libgfortran-5.dll",
    "libgcc_s_seh-1.dll", 
    "libwinpthread-1.dll",
    "libopenblas.dll",
    "python3*.dll"
)

Write-Host "`n🔍 检查PATH中的关键DLL..." -ForegroundColor Cyan

$PathDirs = $env:PATH -split ';'
$DLLConflicts = @()

foreach ($dll in $CriticalDLLs) {
    $found = @()
    foreach ($dir in $PathDirs) {
        if (Test-Path $dir) {
            $matches = Get-ChildItem -Path $dir -Filter $dll -ErrorAction SilentlyContinue
            foreach ($match in $matches) {
                $found += @{
                    Path = $match.FullName
                    Size = $match.Length
                    LastWrite = $match.LastWriteTime
                }
            }
        }
    }
    
    if ($found.Count -gt 1) {
        Write-Host "⚠️  发现 $dll 的多个版本:" -ForegroundColor Yellow
        foreach ($item in $found) {
            Write-Host "   - $($item.Path) ($(($item.Size/1KB).ToString('F1')) KB)" -ForegroundColor Gray
        }
        $DLLConflicts += @{
            DLL = $dll
            Locations = $found
        }
    } elseif ($found.Count -eq 1) {
        Write-Host "✓ $dll -> $($found[0].Path)" -ForegroundColor Green
    } else {
        Write-Host "? $dll 未在PATH中找到" -ForegroundColor Gray
    }
}

# 3. 使用dumpbin检查依赖关系（如果可用）
Write-Host "`n🔍 检查 $TargetExe 的直接依赖..." -ForegroundColor Cyan

try {
    $dumpbinOutput = & dumpbin /DEPENDENTS $TargetExe 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 使用 dumpbin 分析依赖关系" -ForegroundColor Green
        
        $dependencies = @()
        $inDependents = $false
        
        foreach ($line in $dumpbinOutput) {
            if ($line -match "Image has the following dependencies:") {
                $inDependents = $true
                continue
            }
            if ($inDependents -and $line -match "\.dll") {
                $dllName = $line.Trim()
                $dependencies += $dllName
                Write-Host "   依赖: $dllName" -ForegroundColor Gray
            }
            if ($line -match "Summary") {
                break
            }
        }
        
        # 检查依赖的DLL是否在PATH中可找到
        Write-Host "`n🔍 验证依赖DLL的可用性..." -ForegroundColor Cyan
        foreach ($dep in $dependencies) {
            $found = $false
            foreach ($dir in $PathDirs) {
                if (Test-Path $dir) {
                    $depPath = Join-Path $dir $dep
                    if (Test-Path $depPath) {
                        Write-Host "✓ $dep -> $depPath" -ForegroundColor Green
                        $found = $true
                        break
                    }
                }
            }
            if (-not $found) {
                Write-Host "❌ $dep 未找到!" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "⚠️  dumpbin 不可用，跳过依赖分析" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  无法运行 dumpbin: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. 检查MSYS2/MinGW环境
Write-Host "`n🔍 检查MSYS2/MinGW环境..." -ForegroundColor Cyan

$MSYS2Paths = @(
    "C:\msys64\mingw64\bin",
    "C:\msys64\usr\bin", 
    "C:\msys64\mingw32\bin"
)

foreach ($path in $MSYS2Paths) {
    if (Test-Path $path) {
        Write-Host "✓ 找到 MSYS2 路径: $path" -ForegroundColor Green
        
        # 检查关键的编译器DLL
        $CompilerDLLs = @("libgfortran-5.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll")
        foreach ($dll in $CompilerDLLs) {
            $dllPath = Join-Path $path $dll
            if (Test-Path $dllPath) {
                $fileInfo = Get-Item $dllPath
                Write-Host "   ✓ $dll ($(($fileInfo.Length/1KB).ToString('F1')) KB, $($fileInfo.LastWriteTime))" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "? MSYS2 路径不存在: $path" -ForegroundColor Gray
    }
}

# 5. 运行测试并捕获错误
Write-Host "`n🧪 运行测试程序..." -ForegroundColor Cyan

$TestInput = @"
&CONTROL
BulkBand_calc = T
/

&SYSTEM
NSLAB = 10
NumOccupied = 18
SOC = 1
E_FERMI = 6.6556
Bmin= -1.0, Bmax= 1.0, Nk1=50
/

&PARAMETERS
Eta_Arc = 0.001
/

LATTICE
Angstrom
   2.69   0.00   0.00
   0.00   2.69   0.00
   0.00   0.00  10.00

ATOM_POSITIONS
2
Direct
C   0.33333   0.66667   0.50000
C   0.66667   0.33333   0.50000

PROJECTORS
2
C px py pz
C px py pz

SURFACE
1 0 0
0 1 0
"@

# 创建测试输入文件
$TestInput | Out-File -FilePath "wt_test.in" -Encoding ASCII

try {
    # 启动进程并监控
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $TargetExe
    $processInfo.RedirectStandardInput = $true
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    
    Write-Host "启动进程: $TargetExe" -ForegroundColor Yellow
    $process.Start() | Out-Null
    
    # 发送输入
    $process.StandardInput.WriteLine("wt_test.in")
    $process.StandardInput.Close()
    
    # 等待进程完成（最多30秒）
    $completed = $process.WaitForExit(30000)
    
    if ($completed) {
        $exitCode = $process.ExitCode
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        
        Write-Host "进程退出码: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
        
        if ($exitCode -eq -1073740940) {
            Write-Host "❌ 确认堆损坏错误 (0xC0000374)" -ForegroundColor Red
        } elseif ($exitCode -eq 0) {
            Write-Host "✓ 程序正常执行" -ForegroundColor Green
        } else {
            Write-Host "⚠️  程序异常退出" -ForegroundColor Yellow
        }
        
        if ($Detailed) {
            Write-Host "`n--- 标准输出 ---" -ForegroundColor Cyan
            Write-Host $stdout
            Write-Host "`n--- 标准错误 ---" -ForegroundColor Cyan  
            Write-Host $stderr
        }
    } else {
        Write-Host "❌ 进程超时，强制终止" -ForegroundColor Red
        $process.Kill()
    }
    
} catch {
    Write-Host "❌ 运行测试失败: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # 清理
    if (Test-Path "wt_test.in") { Remove-Item "wt_test.in" -Force }
    if (Test-Path "WT.out") { Remove-Item "WT.out" -Force }
}

# 6. 生成报告摘要
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "📋 诊断摘要" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

if ($DLLConflicts.Count -gt 0) {
    Write-Host "`n⚠️  发现 $($DLLConflicts.Count) 个DLL冲突:" -ForegroundColor Yellow
    foreach ($conflict in $DLLConflicts) {
        Write-Host "   • $($conflict.DLL)" -ForegroundColor Red
    }
    
    Write-Host "`n💡 建议解决方案:" -ForegroundColor Green
    Write-Host "   1. 清理PATH环境变量，移除冲突的路径" -ForegroundColor White
    Write-Host "   2. 确保MSYS2/MinGW64路径在PATH前部" -ForegroundColor White
    Write-Host "   3. 重新构建wannier-tools使用静态链接" -ForegroundColor White
} else {
    Write-Host "`n✓ 未发现明显的DLL冲突" -ForegroundColor Green
}

Write-Host "`n🛠️  进一步调试步骤:" -ForegroundColor Cyan
Write-Host "   1. 下载 Dependency Walker: https://dependencywalker.com/" -ForegroundColor White
Write-Host "   2. 使用 Process Monitor 监控文件访问" -ForegroundColor White
Write-Host "   3. 检查Windows事件查看器" -ForegroundColor White
Write-Host "   4. 运行: python debug_dll_conflicts.py" -ForegroundColor White

if ($SaveReport) {
    $reportPath = "dll_check_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    $report = @"
DLL依赖检查报告
生成时间: $(Get-Date)
目标程序: $TargetExe

DLL冲突数量: $($DLLConflicts.Count)
$(if ($DLLConflicts.Count -gt 0) {
    "冲突详情:"
    foreach ($conflict in $DLLConflicts) {
        "- $($conflict.DLL):"
        foreach ($loc in $conflict.Locations) {
            "  $($loc.Path)"
        }
    }
})

系统PATH前10个目录:
$($PathDirs[0..9] | ForEach-Object { "- $_" } | Out-String)
"@
    
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "`n📄 报告已保存到: $reportPath" -ForegroundColor Green
} 
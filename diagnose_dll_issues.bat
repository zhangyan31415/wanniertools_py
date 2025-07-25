@echo off
REM Windows DLL冲突诊断工具启动器
REM 用于诊断wannier-tools的堆损坏问题

echo ========================================
echo    Windows DLL冲突诊断工具
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "wt-py.exe" (
    echo ❌ 错误: 找不到 wt-py.exe
    echo 请在包含 wt-py.exe 的目录中运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✓ 找到 wt-py.exe
echo.

REM 设置调试环境变量
echo 🔧 设置调试环境变量...
set PYTHONFAULTHANDLER=1
set PYTHONDEVMODE=1
set MALLOC_CHECK_=1
echo ✓ 调试环境已设置
echo.

REM 运行Python诊断工具
echo 🔍 运行Python DLL冲突检测器...
echo ========================================
python debug_dll_conflicts.py
echo ========================================
echo.

REM 运行PowerShell诊断工具
echo 🔍 运行PowerShell DLL依赖检查器...
echo ========================================
powershell -ExecutionPolicy Bypass -File check_dll_deps.ps1 -SaveReport
echo ========================================
echo.

REM 收集系统信息
echo 📋 收集系统信息...
echo ========================================

echo --- 系统版本信息 ---
ver

echo.
echo --- Python版本信息 ---
python --version

echo.
echo --- PATH环境变量（前10个目录）---
echo %PATH% | tr ";" "\n" | head -10

echo.
echo --- MSYS2/MinGW检查 ---
if exist "C:\msys64\mingw64\bin" (
    echo ✓ 找到 C:\msys64\mingw64\bin
    dir "C:\msys64\mingw64\bin\libgfortran*.dll" 2>nul
    dir "C:\msys64\mingw64\bin\libgcc*.dll" 2>nul
) else (
    echo ? 未找到 C:\msys64\mingw64\bin
)

echo.
echo --- 检查关键DLL ---
where libgfortran-5.dll 2>nul
where libgcc_s_seh-1.dll 2>nul
where python3*.dll 2>nul

echo ========================================
echo.

REM 提供下一步建议
echo 💡 下一步建议:
echo.
echo 1. 查看生成的报告文件:
echo    - dll_conflict_report.json
echo    - dll_check_report_*.txt
echo.
echo 2. 如果发现DLL冲突，请:
echo    - 备份当前PATH环境变量
echo    - 清理PATH中的冲突路径
echo    - 确保MSYS2/MinGW64在PATH前部
echo.
echo 3. 如果问题持续，尝试重新构建:
echo    pip uninstall wannier-tools
echo    pip cache purge
echo    pip install . --no-cache-dir
echo.
echo 4. 使用外部工具进一步分析:
echo    - Dependency Walker: https://dependencywalker.com/
echo    - Process Monitor: https://docs.microsoft.com/sysinternals
echo.

pause 
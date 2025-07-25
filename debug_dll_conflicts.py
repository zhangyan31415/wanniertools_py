#!/usr/bin/env python3
"""
Windows DLL冲突检测和调试工具
用于诊断wannier-tools在Windows上的DLL加载问题和冲突
"""

import os
import sys
import subprocess
import json
import ctypes
import ctypes.wintypes
from pathlib import Path
import time
import traceback
from typing import List, Dict, Optional, Tuple

class DLLConflictDetector:
    """DLL冲突检测器"""
    
    def __init__(self):
        self.report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {},
            "dll_analysis": {},
            "conflicts": [],
            "recommendations": []
        }
        
    def get_system_info(self):
        """获取系统信息"""
        try:
            import platform
            self.report["system_info"] = {
                "platform": platform.platform(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "python_executable": sys.executable
            }
            
            # 获取PATH环境变量
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            self.report["system_info"]["path_directories"] = path_dirs[:10]  # 只显示前10个
            
            print("✓ 系统信息收集完成")
            
        except Exception as e:
            print(f"✗ 系统信息收集失败: {e}")
    
    def check_process_dlls(self, process_name: str = None) -> Dict:
        """使用PowerShell检查进程加载的DLL"""
        dll_info = {"loaded_dlls": [], "error": None}
        
        try:
            if process_name:
                # 检查特定进程
                ps_cmd = f'''
                Get-Process -Name "{process_name}" -ErrorAction SilentlyContinue | 
                ForEach-Object {{ 
                    $_.Modules | Select-Object ModuleName, FileName, Size 
                }} | ConvertTo-Json
                '''
            else:
                # 检查当前Python进程
                pid = os.getpid()
                ps_cmd = f'''
                Get-Process -Id {pid} -ErrorAction SilentlyContinue | 
                ForEach-Object {{ 
                    $_.Modules | Select-Object ModuleName, FileName, Size 
                }} | ConvertTo-Json
                '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    dlls = json.loads(result.stdout)
                    if isinstance(dlls, dict):
                        dlls = [dlls]
                    dll_info["loaded_dlls"] = dlls
                except json.JSONDecodeError:
                    dll_info["error"] = "JSON解析失败"
            else:
                dll_info["error"] = result.stderr
                
        except subprocess.TimeoutExpired:
            dll_info["error"] = "PowerShell命令超时"
        except Exception as e:
            dll_info["error"] = str(e)
            
        return dll_info
    
    def check_dll_dependencies(self, dll_path: str) -> List[str]:
        """检查DLL依赖关系"""
        dependencies = []
        
        try:
            # 使用dumpbin或objdump检查依赖
            for tool in ["dumpbin", "objdump"]:
                try:
                    if tool == "dumpbin":
                        cmd = [tool, "/DEPENDENTS", dll_path]
                    else:
                        cmd = [tool, "-p", dll_path]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # 解析输出获取依赖DLL
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if '.dll' in line.lower():
                                dll_name = line.strip().split()[-1]
                                if dll_name.endswith('.dll'):
                                    dependencies.append(dll_name)
                        break
                except FileNotFoundError:
                    continue
                    
        except Exception as e:
            print(f"检查DLL依赖失败: {e}")
            
        return list(set(dependencies))  # 去重
    
    def find_dll_conflicts(self) -> List[Dict]:
        """查找DLL冲突"""
        conflicts = []
        
        # 常见的冲突DLL列表
        critical_dlls = [
            "msvcrt.dll", "msvcp140.dll", "vcruntime140.dll",
            "libgfortran-5.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll",
            "libopenblas.dll", "liblapack.dll", "libblas.dll",
            "python3.dll", "python39.dll", "python310.dll", "python311.dll", "python312.dll"
        ]
        
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        for dll_name in critical_dlls:
            found_locations = []
            
            for path_dir in path_dirs:
                if not path_dir or not os.path.exists(path_dir):
                    continue
                    
                dll_path = os.path.join(path_dir, dll_name)
                if os.path.exists(dll_path):
                    try:
                        stat = os.stat(dll_path)
                        found_locations.append({
                            "path": dll_path,
                            "size": stat.st_size,
                            "mtime": time.ctime(stat.st_mtime)
                        })
                    except OSError:
                        continue
            
            if len(found_locations) > 1:
                conflicts.append({
                    "dll_name": dll_name,
                    "conflict_type": "multiple_versions",
                    "locations": found_locations,
                    "severity": "high" if "fortran" in dll_name.lower() or "gcc" in dll_name.lower() else "medium"
                })
        
        return conflicts
    
    def check_wannier_tools_dlls(self):
        """检查wannier-tools相关的DLL"""
        wt_dll_info = {"status": "unknown", "details": {}}
        
        try:
            # 尝试导入wannier_tools
            import wannier_tools
            wt_dll_info["status"] = "imported_successfully"
            wt_dll_info["details"]["version"] = getattr(wannier_tools, '__version__', 'unknown')
            wt_dll_info["details"]["location"] = wannier_tools.__file__
            
            # 检查wannier_tools目录下的DLL文件
            wt_dir = Path(wannier_tools.__file__).parent
            dll_files = list(wt_dir.rglob("*.dll"))
            wt_dll_info["details"]["bundled_dlls"] = [str(dll) for dll in dll_files]
            
        except ImportError as e:
            wt_dll_info["status"] = "import_failed"
            wt_dll_info["details"]["error"] = str(e)
        except Exception as e:
            wt_dll_info["status"] = "error"
            wt_dll_info["details"]["error"] = str(e)
            
        return wt_dll_info
    
    def run_wt_with_dll_monitoring(self) -> Dict:
        """运行wt-py并监控DLL加载"""
        monitoring_result = {
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "dll_snapshot_before": {},
            "dll_snapshot_after": {},
            "execution_time": 0
        }
        
        try:
            # 获取执行前的DLL快照
            monitoring_result["dll_snapshot_before"] = self.check_process_dlls()
            
            # 创建一个简单的测试输入文件
            test_input = """
&CONTROL
BulkBand_calc         = T
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
"""
            
            with open("wt_test.in", "w") as f:
                f.write(test_input)
            
            start_time = time.time()
            
            # 运行wt-py
            result = subprocess.run(
                ["wt-py.exe"], 
                input="wt_test.in\n",
                capture_output=True, 
                text=True, 
                timeout=60,
                cwd=os.getcwd()
            )
            
            end_time = time.time()
            monitoring_result["execution_time"] = end_time - start_time
            monitoring_result["exit_code"] = result.returncode
            monitoring_result["stdout"] = result.stdout
            monitoring_result["stderr"] = result.stderr
            
            # 获取执行后的DLL快照
            monitoring_result["dll_snapshot_after"] = self.check_process_dlls()
            
        except subprocess.TimeoutExpired:
            monitoring_result["exit_code"] = "TIMEOUT"
            monitoring_result["stderr"] = "程序执行超时"
        except FileNotFoundError:
            monitoring_result["exit_code"] = "NOT_FOUND"
            monitoring_result["stderr"] = "wt-py.exe 未找到"
        except Exception as e:
            monitoring_result["exit_code"] = "ERROR"
            monitoring_result["stderr"] = str(e)
        finally:
            # 清理测试文件
            for file in ["wt_test.in", "WT.out"]:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except:
                        pass
        
        return monitoring_result
    
    def generate_recommendations(self):
        """生成修复建议"""
        recommendations = []
        
        # 基于冲突分析生成建议
        if self.report["conflicts"]:
            recommendations.append({
                "priority": "high",
                "category": "dll_conflicts",
                "title": "解决DLL冲突",
                "description": "检测到多个版本的关键DLL，建议清理PATH环境变量",
                "actions": [
                    "备份当前PATH环境变量",
                    "移除不必要的路径，特别是包含旧版本编译器的路径",
                    "确保MSYS2/MinGW64路径在PATH前部",
                    "重启命令提示符或系统"
                ]
            })
        
        # 检查是否需要重新构建
        wt_info = self.report.get("dll_analysis", {}).get("wannier_tools", {})
        if wt_info.get("status") == "import_failed":
            recommendations.append({
                "priority": "high", 
                "category": "rebuild",
                "title": "重新构建wannier-tools",
                "description": "wannier-tools导入失败，可能需要重新构建",
                "actions": [
                    "清理构建缓存: pip cache purge",
                    "卸载现有版本: pip uninstall wannier-tools",
                    "重新安装: pip install . --no-cache-dir",
                    "或使用静态链接版本重新构建"
                ]
            })
        
        # 通用调试建议
        recommendations.append({
            "priority": "medium",
            "category": "debugging",
            "title": "启用详细调试",
            "description": "收集更多调试信息",
            "actions": [
                "设置环境变量: set PYTHONFAULTHANDLER=1",
                "使用Process Monitor监控文件访问",
                "使用Dependency Walker检查DLL依赖",
                "在调试模式下运行: python -X dev"
            ]
        })
        
        self.report["recommendations"] = recommendations
    
    def run_full_analysis(self) -> Dict:
        """运行完整的DLL冲突分析"""
        print("🔍 开始DLL冲突检测分析...")
        print("=" * 60)
        
        # 1. 收集系统信息
        print("1. 收集系统信息...")
        self.get_system_info()
        
        # 2. 检查DLL冲突
        print("2. 检查DLL冲突...")
        conflicts = self.find_dll_conflicts()
        self.report["conflicts"] = conflicts
        
        if conflicts:
            print(f"   ⚠️  发现 {len(conflicts)} 个DLL冲突")
            for conflict in conflicts:
                print(f"      - {conflict['dll_name']}: {len(conflict['locations'])} 个版本")
        else:
            print("   ✓ 未发现明显的DLL冲突")
        
        # 3. 检查wannier-tools DLL
        print("3. 检查wannier-tools状态...")
        wt_info = self.check_wannier_tools_dlls()
        self.report["dll_analysis"]["wannier_tools"] = wt_info
        print(f"   状态: {wt_info['status']}")
        
        # 4. 运行测试并监控DLL
        print("4. 运行wannier-tools测试...")
        monitoring = self.run_wt_with_dll_monitoring()
        self.report["dll_analysis"]["execution_test"] = monitoring
        
        if monitoring["exit_code"] == -1073740940:
            print("   ❌ 确认复现了堆损坏错误 (0xC0000374)")
        elif monitoring["exit_code"] == 0:
            print("   ✓ 程序正常退出")
        else:
            print(f"   ⚠️  程序异常退出，代码: {monitoring['exit_code']}")
        
        # 5. 生成建议
        print("5. 生成修复建议...")
        self.generate_recommendations()
        
        print("=" * 60)
        print("🔍 分析完成!")
        
        return self.report
    
    def save_report(self, filename: str = "dll_conflict_report.json"):
        """保存分析报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
            print(f"📄 报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
    
    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "=" * 60)
        print("📋 DLL冲突分析摘要")
        print("=" * 60)
        
        # 冲突摘要
        conflicts = self.report.get("conflicts", [])
        if conflicts:
            print(f"\n⚠️  发现 {len(conflicts)} 个DLL冲突:")
            for conflict in conflicts:
                print(f"   • {conflict['dll_name']} ({conflict['severity']} 严重性)")
                for loc in conflict["locations"]:
                    print(f"     - {loc['path']}")
        else:
            print("\n✓ 未发现DLL冲突")
        
        # wannier-tools状态
        wt_status = self.report.get("dll_analysis", {}).get("wannier_tools", {}).get("status", "unknown")
        print(f"\n📦 wannier-tools状态: {wt_status}")
        
        # 执行测试结果
        exec_test = self.report.get("dll_analysis", {}).get("execution_test", {})
        exit_code = exec_test.get("exit_code")
        if exit_code == -1073740940:
            print("❌ 确认存在堆损坏问题")
        elif exit_code == 0:
            print("✓ 测试执行成功")
        else:
            print(f"⚠️  测试异常退出: {exit_code}")
        
        # 建议
        recommendations = self.report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 修复建议 ({len(recommendations)} 条):")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['title']} ({rec['priority']} 优先级)")


def main():
    """主函数"""
    if os.name != 'nt':
        print("❌ 此工具仅支持Windows系统")
        return
    
    detector = DLLConflictDetector()
    
    try:
        # 运行完整分析
        report = detector.run_full_analysis()
        
        # 保存报告
        detector.save_report()
        
        # 打印摘要
        detector.print_summary()
        
        # 提供进一步的调试建议
        print("\n" + "=" * 60)
        print("🛠️  进一步调试建议:")
        print("=" * 60)
        print("1. 下载并使用 Dependency Walker:")
        print("   https://dependencywalker.com/")
        print("   分析 wt-py.exe 的DLL依赖关系")
        print()
        print("2. 使用 Process Monitor 监控文件访问:")
        print("   https://docs.microsoft.com/en-us/sysinternals/downloads/procmon")
        print()
        print("3. 检查事件查看器中的应用程序错误日志")
        print()
        print("4. 如果问题持续，考虑在虚拟环境中重新构建:")
        print("   conda create -n wt-debug python=3.9")
        print("   conda activate wt-debug")
        print("   pip install . --no-cache-dir")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断分析")
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main() 
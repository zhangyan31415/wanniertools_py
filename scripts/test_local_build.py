#!/usr/bin/env python3
"""
本地构建测试脚本
用于在推送到GitHub之前验证配置是否正确
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"🔄 运行命令: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(f"📤 输出: {result.stdout}")
        if result.stderr:
            print(f"⚠️  错误: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {e}")
        if not check:
            return e
        raise

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    # 检查Python版本
    py_version = platform.python_version()
    print(f"Python版本: {py_version}")
    
    # 检查必要的工具
    tools = ['pip', 'git']
    for tool in tools:
        result = run_command(f"which {tool}", check=False)
        if result.returncode == 0:
            print(f"✅ {tool}: 已安装")
        else:
            print(f"❌ {tool}: 未找到")
            return False
    
    return True

def test_build_system():
    """测试构建系统"""
    print("\n🏗️  测试构建系统...")
    
    # 检查项目文件
    required_files = [
        'pyproject.toml',
        'meson.build',
        'src/wannier_tools/__init__.py',
        'src/wannier_tools/_fortran_src/main.f90'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少文件: {file}")
            return False
        else:
            print(f"✅ 找到文件: {file}")
    
    return True

def test_python_import():
    """测试Python包结构"""
    print("\n🐍 测试Python包结构...")
    
    # 检查Python路径
    sys.path.insert(0, str(Path('src').absolute()))
    
    try:
        import wannier_tools
        print(f"✅ 成功导入wannier_tools")
        print(f"   版本: {wannier_tools.__version__}")
        print(f"   路径: {wannier_tools.__file__}")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_cibuildwheel_locally():
    """本地测试cibuildwheel配置"""
    print("\n🔧 测试cibuildwheel配置...")
    
    # 检查是否安装了cibuildwheel
    result = run_command("pip list | grep cibuildwheel", check=False)
    if result.returncode != 0:
        print("⚠️  cibuildwheel未安装，尝试安装...")
        run_command("pip install cibuildwheel")
    
    # 显示cibuildwheel配置
    print("📋 cibuildwheel将构建的轮子:")
    result = run_command("cibuildwheel --print-build-identifiers", check=False)
    
    return True

def test_docker_setup():
    """测试Docker设置（仅Linux）"""
    if platform.system() != 'Linux':
        print(f"⏭️  跳过Docker测试（当前系统: {platform.system()}）")
        return True
    
    print("\n🐳 测试Docker设置...")
    
    # 检查Docker
    result = run_command("docker --version", check=False)
    if result.returncode != 0:
        print("❌ Docker未安装或未运行")
        return False
    
    # 检查Dockerfile
    if not Path('build_support/Dockerfile.manylinux-openmpi').exists():
        print("❌ 缺少Dockerfile: build_support/Dockerfile.manylinux-openmpi")
        return False
    
    print("✅ Docker环境检查通过")
    return True

def main():
    """主函数"""
    print("🚀 WannierTools 本地构建测试")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 工作目录: {project_root.absolute()}")
    
    tests = [
        ("依赖检查", check_dependencies),
        ("构建系统检查", test_build_system),
        ("Python包检查", test_python_import),
        ("cibuildwheel配置检查", test_cibuildwheel_locally),
        ("Docker设置检查", test_docker_setup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
        except Exception as e:
            print(f"💥 {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n{'='*20} 测试总结 {'='*20}")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！您可以推送到GitHub开始CI构建了。")
        print("💡 建议:")
        print("   1. git add -A")
        print("   2. git commit -m 'Update CI configuration for cross-platform builds'")
        print("   3. git push")
    else:
        print("\n⚠️  部分测试失败，请修复后再推送到GitHub。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
GitHub Actions 快速启动脚本
帮助用户快速开始GitHub Actions CI/CD构建流程
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令"""
    print(f"🔄 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def check_git_status():
    """检查Git状态"""
    print("📋 检查Git状态...")
    
    # 检查是否有未提交的更改
    result = subprocess.run(
        "git status --porcelain", 
        shell=True, 
        capture_output=True, 
        text=True
    )
    
    if result.stdout.strip():
        print("📝 发现未提交的更改:")
        print(result.stdout)
        return True
    else:
        print("✅ 工作目录干净，没有未提交的更改")
        return False

def show_build_preview():
    """显示构建预览"""
    print("\n🎯 构建预览:")
    print("=" * 50)
    
    # 显示将要构建的轮子
    result = subprocess.run(
        "cibuildwheel --print-build-identifiers", 
        shell=True, 
        capture_output=True, 
        text=True,
        check=False
    )
    
    if result.returncode == 0:
        wheels = result.stdout.strip().split('\n')
        print(f"📦 将构建 {len(wheels)} 个Linux轮子:")
        for wheel in wheels:
            print(f"   • {wheel}")
        
        print(f"\n🔢 总预计轮子数量:")
        print(f"   • Linux (x86_64): {len(wheels)} 个")
        print(f"   • macOS (x86_64 + arm64): {len(wheels) * 2} 个")
        print(f"   • Windows (AMD64): {len(wheels)} 个")
        print(f"   • 🎉 总计: {len(wheels) * 4} 个轮子")
    else:
        print("⚠️  无法预览构建配置")

def commit_and_push():
    """提交并推送代码"""
    print("\n🚀 准备提交并推送代码...")
    
    # 添加所有更改
    if not run_command("git add -A"):
        return False
    
    # 创建提交
    commit_msg = "feat: setup cross-platform CI/CD with cibuildwheel\n\n" \
                "- Configure GitHub Actions for Linux, macOS, Windows builds\n" \
                "- Support Python 3.8-3.12 across all platforms\n" \
                "- Add comprehensive testing and artifact collection\n" \
                "- Include MPI functionality testing"
    
    if not run_command(f'git commit -m "{commit_msg}"'):
        print("⚠️  提交失败，可能没有更改需要提交")
        return False
    
    # 推送到远程
    print("📤 推送到GitHub...")
    if not run_command("git push"):
        print("❌ 推送失败，请检查Git配置和权限")
        return False
    
    return True

def show_next_steps():
    """显示后续步骤"""
    print("\n🎉 配置完成！后续步骤:")
    print("=" * 50)
    
    # 获取远程仓库URL
    result = subprocess.run(
        "git config --get remote.origin.url", 
        shell=True, 
        capture_output=True, 
        text=True,
        check=False
    )
    
    if result.returncode == 0:
        repo_url = result.stdout.strip()
        # 转换SSH URL为HTTPS URL
        if repo_url.startswith("git@github.com:"):
            repo_url = repo_url.replace("git@github.com:", "https://github.com/")
            repo_url = repo_url.replace(".git", "")
        
        actions_url = f"{repo_url}/actions"
        
        print(f"1. 🌐 访问GitHub Actions: {actions_url}")
        print("2. 🔍 查找 'Build and Test WannierTools Cross-Platform Wheels' workflow")
        print("3. ⏱️  等待构建完成 (约60-75分钟)")
        print("4. 📦 下载构建的轮子 (在Artifacts部分)")
        
        print(f"\n📊 监控构建状态:")
        print(f"   • 总体进度: {actions_url}")
        print(f"   • 构建日志: 点击具体的workflow运行")
        
        print(f"\n🔧 如需调试:")
        print(f"   • 查看失败的job日志")
        print(f"   • 修改配置后重新推送")
        print(f"   • 使用 'workflow_dispatch' 手动触发")
        
    else:
        print("1. 🌐 前往您的GitHub仓库")
        print("2. 🔍 点击 'Actions' 标签")
        print("3. ⏱️  查看构建进度")

def main():
    """主函数"""
    print("🚀 WannierTools GitHub Actions 快速启动")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if not Path('.git').exists():
        print("❌ 错误: 不在Git仓库中，请先初始化Git仓库")
        return False
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 项目目录: {project_root.absolute()}")
    
    # 检查Git状态
    has_changes = check_git_status()
    
    # 显示构建预览
    show_build_preview()
    
    if has_changes:
        print(f"\n❓ 是否要提交并推送代码到GitHub启动CI构建？")
        response = input("   输入 'y' 或 'yes' 继续: ").lower().strip()
        
        if response in ['y', 'yes']:
            if commit_and_push():
                show_next_steps()
                print("\n✅ 成功！GitHub Actions CI构建已启动")
                return True
            else:
                print("\n❌ 失败！请检查错误信息")
                return False
        else:
            print("\n⏭️  已取消，您可以稍后手动提交并推送")
            return True
    else:
        print(f"\n💡 没有新的更改需要提交")
        print(f"   如果您已经推送过代码，请直接查看GitHub Actions")
        show_next_steps()
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
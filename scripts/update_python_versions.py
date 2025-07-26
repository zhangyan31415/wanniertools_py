#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新Python版本配置脚本

使用方法:
    python scripts/update_python_versions.py "3.9 3.10 3.11"

这个脚本会自动更新:
1. build_support/Dockerfile.manylinux-openmpi
2. pyproject.toml

确保所有文件使用相同的Python版本配置。
"""

import sys
import re
import os
from pathlib import Path

def update_dockerfile(python_versions):
    """更新Dockerfile中的Python版本循环"""
    dockerfile_path = Path("build_support/Dockerfile.manylinux-openmpi")
    
    if not dockerfile_path.exists():
        print(f"❌ 文件不存在: {dockerfile_path}")
        return False
    
    # 生成Docker格式: cp3{9,10,11}-*
    version_numbers = [v.replace(".", "") for v in python_versions]
    short_numbers = [v[1:] for v in version_numbers]  # 去掉开头的3
    docker_pattern = f"cp3{{{','.join(short_numbers)}}}-*"
    
    # 读取文件
    content = dockerfile_path.read_text()
    
    # 查找并替换Python版本循环行
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'RUN for PYBIN_DIR in /opt/python/cp3{' in line and '}-*/bin; do \\' in line:
            lines[i] = f'RUN for PYBIN_DIR in /opt/python/{docker_pattern}/bin; do \\'
            break
    
    new_content = '\n'.join(lines)
    
    if new_content != content:
        dockerfile_path.write_text(new_content)
        print(f"✅ 已更新 {dockerfile_path}: {docker_pattern}")
        return True
    else:
        print(f"ℹ️  {dockerfile_path} 无需更新")
        return True

def update_pyproject_toml(python_versions):
    """更新pyproject.toml中的构建版本"""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print(f"❌ 文件不存在: {pyproject_path}")
        return False
    
    # 生成pyproject格式: ["cp39-*", "cp310-*", "cp311-*"]
    version_numbers = [v.replace(".", "") for v in python_versions]
    cibw_versions = [f'"cp{v}-*"' for v in version_numbers]
    pyproject_format = f'[{", ".join(cibw_versions)}]'
    
    # 读取文件
    content = pyproject_path.read_text()
    
    # 替换build配置
    pattern = r'build = \[.*?\]'
    replacement = f'build = {pyproject_format}'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        pyproject_path.write_text(new_content)
        print(f"✅ 已更新 {pyproject_path}: {pyproject_format}")
        return True
    else:
        print(f"ℹ️  {pyproject_path} 无需更新")
        return True

def main():
    if len(sys.argv) != 2:
        print("❌ 用法: python scripts/update_python_versions.py \"3.9 3.10 3.11\"")
        sys.exit(1)
    
    python_versions_str = sys.argv[1]
    python_versions = python_versions_str.split()
    
    print(f"🎯 更新Python版本配置: {python_versions}")
    
    # 验证版本格式
    for version in python_versions:
        if not re.match(r'^\d+\.\d+$', version):
            print(f"❌ 无效的Python版本格式: {version}")
            sys.exit(1)
    
    # 更新文件
    success = True
    success &= update_dockerfile(python_versions)
    success &= update_pyproject_toml(python_versions)
    
    if success:
        print("✅ 所有文件更新完成！")
        print("\n📋 下一步:")
        print("1. 检查 .github/workflows/build_wheels.yml 中的 PYTHON_VERSIONS_SOURCE")
        print("2. 提交更改: git add . && git commit -m 'Update Python versions'")
    else:
        print("❌ 更新过程中出现错误")
        sys.exit(1)

if __name__ == "__main__":
    main() 
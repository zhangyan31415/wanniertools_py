# WannierTools

WannierTools: An open-source software package for novel topological materials

## 🚀 **GitHub Actions 自动化构建**

本项目使用 **GitHub Actions + cibuildwheel** 实现全自动多平台 wheel 构建：

### ✨ **核心优势**
- 🎯 **一键构建**: Push 代码自动构建所有平台
- 🌍 **全平台支持**: Linux、macOS、Windows (Python 3.9-3.12)
- 🔄 **运行时 MPI**: 无编译依赖，最大兼容性
- 📦 **自动发布**: Tag 版本自动发布到 PyPI

### 🛠️ **使用方法**
1. **自动构建**: Push 到 main/master 分支
2. **测试构建**: GitHub Actions → "Test Build" → 手动触发
3. **发布版本**: 创建 `v*` 标签自动发布

## 快速开始

### 安装

从 PyPI 安装（推荐）：
```bash
pip install wannier-tools
```

从源码安装：
```bash
git clone <your-repo>
cd wannier_tools_pip
pip install .
```

#### Linux用户（推荐）
```bash
mamba create -n wannier-tools python=3.9 numpy -y
mamba activate wannier-tools
mamba install openmpi -y
pip install wannier_tools-2.7.1-cp39-cp39-linux_x86_64.whl
```

#### macOS用户
```bash
mamba create -n wannier-tools python=3.9 numpy -y
mamba activate wannier-tools
mamba install openmpi -y
pip install wannier_tools-2.7.1-cp39-cp39-macosx_*.whl
```

#### Windows用户
```bash
mamba create -n wannier-tools python=3.9 numpy -y
mamba activate wannier-tools
pip install wannier_tools-2.7.1-cp39-cp39-win_*.whl
```

### 使用

```bash
# 激活环境
mamba activate wannier-tools

# 运行WannierTools
wt-py -i input_file.in

# 并行运行（Linux/macOS）
mpirun -np 4 wt-py -i input_file.in
```

## 平台支持

| 功能 | Linux | macOS | Windows |
|------|-------|-------|---------|
| 串行计算 | ✅ | ✅ | ✅ |
| MPI并行计算 | ✅ | ✅ | ❌ |
| 高性能计算 | ✅ | ⚠️ | ❌ |

## 文档

- [用户安装指南](docs/user/USER_INSTALL_GUIDE.md) - 详细的安装和使用说明
- [Windows安装指南](docs/user/WINDOWS_INSTALL_GUIDE.md) - Windows特定安装说明
- [开发者指南](docs/developer/WHEEL_RELEASE_GUIDE.md) - 构建和发布说明
- [Windows构建指南](docs/developer/WINDOWS_BUILD_GUIDE.md) - Windows构建说明

## 构建

### 自动化构建（推荐）

#### 使用cibuildwheel
```bash
# 构建所有Python版本
python scripts/build/build_with_cibuildwheel.py

# 或直接使用cibuildwheel
cibuildwheel --platform linux --output-dir wheelhouse
```

#### GitHub Actions
```bash
# 推送标签触发自动构建
git tag v2.7.1
git push origin v2.7.1
```

### 手动构建
```bash
# 多平台构建
python scripts/build/build_multi_platform.py

# 或手动构建
rm -rf build/ dist/ *.egg-info/ .mesonpy_build/
python -m build --wheel
```

## 特性

- **多平台支持**: Linux、macOS、Windows
- **并行计算**: Linux/macOS支持MPI并行
- **易于安装**: 预编译wheel包，无需复杂编译
- **完整功能**: 支持所有WannierTools功能

## 系统要求

- Python 3.8-3.11
- NumPy >= 1.20.0
- MPI运行时（Linux/macOS，用于并行计算）

## 许可证

GPL-3.0-or-later

## 更多信息

- 官方网站: https://www.wanniertools.com/
- 问题反馈: https://github.com/quanshengwu/wannier_tools/issues # wanniertools_py

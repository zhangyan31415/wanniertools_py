# WannierTools MPI 版本开发者手册

## 🎯 **最佳实践：GitHub Actions 自动化构建**

**推荐方式**：使用 GitHub Actions + cibuildwheel 进行自动化多平台构建，这是业界标准的最佳实践！

### ✨ **GitHub Actions 优势**
- 🚀 **零配置烦恼**: 云端自动构建，无需本地环境配置
- 🌍 **真正多平台**: Linux、macOS、Windows 并行构建
- 🔄 **多版本支持**: Python 3.9-3.12 一次性构建
- 📦 **自动发布**: 创建 tag 自动发布到 PyPI
- 🧪 **自动测试**: 包含 MPI 并行功能验证

### 🛠️ **使用方法**
1. **Push 代码** → 自动构建所有平台 wheel
2. **手动测试** → GitHub Actions → "Test Build" workflow
3. **发布版本** → 创建 `v*` 标签 → 自动发布到 PyPI

---

## 📋 备用方案：本地构建
如果需要本地构建（调试、定制等），参考以下章节：

### 目录
1. [环境准备](#环境准备)
2. [Docker 镜像构建](#docker-镜像构建)
3. [跨平台构建](#跨平台构建)
4. [测试验证](#测试验证)
5. [开发工作流](#开发工作流)
6. [故障排除](#故障排除)

## 🛠️ 环境准备

### 基本要求
- Python 3.9+
- Git
- 足够的磁盘空间（至少 10GB 用于构建）

### 平台特定要求

#### Linux
```bash
# 安装 Docker（用于 manylinux 构建）
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER
# 重新登录或重启终端

# 安装构建工具
pip install cibuildwheel build meson ninja
```

#### macOS
```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install gcc python
pip install cibuildwheel build meson ninja
```

#### Windows
```powershell
# 安装 Visual Studio Build Tools
# 下载并安装：https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 安装 Python 依赖
pip install cibuildwheel build meson ninja
```

## 🐳 Docker 镜像构建

### ⚠️ 重要：Linux 用户首次使用必须构建 Docker 镜像

**是的，您记得没错！Linux 平台构建 manylinux wheel 需要 Docker 命令！**

这是因为：
1. manylinux 标准要求在特定的 Linux 环境中构建
2. 我们需要自定义 Docker 镜像以支持运行时 MPI 检测
3. cibuildwheel 会自动使用我们构建的 Docker 镜像

```bash
# 1. 构建支持运行时 MPI 检测的 Docker 镜像
docker build -t wanniertools-builder-nompi -f Dockerfile.manylinux-nompi .

# 2. 验证镜像构建成功
docker images | grep wanniertools-builder-nompi
```

**注意**: macOS 和 Windows 用户不需要 Docker，cibuildwheel 会使用系统原生工具链。

### Docker 镜像说明
- **镜像名称**: `wanniertools-builder-nompi`
- **基础镜像**: `quay.io/pypa/manylinux2014_x86_64`
- **预装依赖**: gcc, gfortran, openblas, arpack
- **特点**: 无 MPI 编译依赖，支持运行时检测

## 🔧 跨平台构建

### 自动化构建脚本

项目提供了智能构建脚本，自动处理临时目录和平台差异：

```bash
# 查看当前平台构建信息
python scripts/cross_platform_info.py

# 跨平台兼容性验证
python scripts/validate_cross_platform.py
```

### 构建命令

#### Linux 构建

**为什么 Linux 用 Docker？**
- manylinux 标准要求特定的 Linux 环境
- 确保跨 Linux 发行版兼容性
- 静态链接和符号版本控制

```bash
# 1. 构建 Docker 镜像（首次必须）
docker build -t wanniertools-builder-nompi -f Dockerfile.manylinux-nompi .

# 2. 构建多个 Python 版本
python scripts/build/build_with_cibuildwheel.py --platform linux --all-pythons --build-only

# 3. 构建单个版本
python scripts/build/build_with_cibuildwheel.py --platform linux --python cp39 --build-only
```

#### macOS 构建

**为什么 macOS 不用 Docker？**
- Docker 在 macOS 上性能差（运行在虚拟机中）
- manylinux 是 Linux 专用标准
- macOS 有自己的二进制兼容机制

**🎯 最完美解决方案 - 多版本原生构建：**

```bash
# 1. 查看可用的 Python 版本
python scripts/build_multi_platform.py --list-pythons

# 2. 构建多个 Python 版本（推荐）
python scripts/build_multi_platform.py --pythons cp39,cp310,cp311,cp312

# 3. 构建单个版本
python scripts/build_multi_platform.py --pythons cp310

# 4. 传统方式（可能有版本问题）
python scripts/build/build_with_cibuildwheel.py --platform macos --native --build-only
```

**优势**：
- ✅ 支持任意 Python 版本（conda、pyenv、官方版本）
- ✅ 自动检测系统安装的多个 Python
- ✅ 正确设置 Homebrew 库路径
- ✅ 一次性构建多个版本

#### Windows 构建

**为什么 Windows 不用 Docker？**
- Windows 容器兼容性复杂
- Visual Studio 工具链已足够
- cibuildwheel 自动下载官方 Python

```bash
# 1. 确保安装 Visual Studio Build Tools
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. 构建多个 Python 版本（自动下载 Python）
python scripts/build/build_with_cibuildwheel.py --platform windows --all-pythons --build-only

# 3. 构建单个版本
python scripts/build/build_with_cibuildwheel.py --platform windows --python cp39 --build-only
```

### 🗂️ 临时目录管理

构建脚本会自动管理临时目录：

#### 自动检测逻辑
1. **Linux**: 使用 `/data/work/zy/temp/wt_wheel` (如果存在)
2. **macOS**: 使用 `/tmp/wt_wheel`
3. **Windows**: 使用 `%TEMP%\wt_wheel`
4. **通用后备**: 使用系统临时目录

#### 手动指定临时目录
```bash
# 设置环境变量
export WT_TEMP_DIR="/your/custom/temp/path"
python scripts/build/build_with_cibuildwheel.py --platform linux --python cp39
```

#### 磁盘空间要求
- **最小**: 5GB
- **推荐**: 10GB
- **完整构建**: 20GB+

### 构建输出

成功构建后，wheel 包将保存在：
```
wheelhouse/
└── wannier_tools-2.7.1-cp39-cp39-[platform]_[arch].whl
```

## 🧪 测试验证

### 基本测试
```bash
# 安装构建的 wheel
pip install wheelhouse/wannier_tools-*.whl

# 基本功能测试
python scripts/test_wheel.py
```

### MPI 并行测试

#### 安装 MPI（仅用于测试）
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install openmpi-bin

# macOS
brew install open-mpi

# CentOS/RHEL
sudo yum install openmpi openmpi-devel
```

#### 测试命令
```bash
cd wannier_tools/examples/Haldane_model

# 单核串行测试
wt-py
grep "CPU cores" WT.out  # 应显示 "1 CPU cores"

# 双核并行测试
mpirun -np 2 wt-py
grep "CPU cores" WT.out  # 应显示 "2 CPU cores"

# 四核并行测试
mpirun -np 4 wt-py
grep "CPU cores" WT.out  # 应显示 "4 CPU cores"
```

### 预期测试结果
- ✅ **无 MPI 环境**: 自动使用 1 CPU 核心
- ✅ **MPI 环境**: 自动检测并使用指定核心数
- ✅ **跨平台兼容**: 相同 wheel 在不同系统运行

## 🔄 开发工作流

### 1. 代码修改流程
```bash
# 1. 修改源代码
vim src/wannier_tools/_fortran_src/your_file.f90

# 2. 验证构建配置
python scripts/validate_cross_platform.py

# 3. 本地快速测试构建
python -m build . --wheel --outdir=test_build

# 4. 完整平台构建
python scripts/build/build_with_cibuildwheel.py --platform [your_platform] --python cp39
```

### 2. 新平台支持
要添加新平台支持，修改 `scripts/build/build_with_cibuildwheel.py`:
```python
elif platform_name == 'your_new_platform':
    # 配置新平台的构建环境
    env_vars['CIBW_BUILD_FRONTEND'] = 'build'
    env_vars['CIBW_CONFIG_SETTINGS'] = 'setup-args=-Dforce_no_mpi=true'
    # ... 其他配置
```

### 3. MPI 检测增强
要支持新的 MPI 实现，修改 `src/wannier_tools/_fortran_src/runtime_mpi.f90`:
```fortran
! 在 check_mpi_environment 函数中添加新的环境变量检测
call get_environment_variable('YOUR_MPI_RANK_VAR', env_var, status)
if (len_trim(env_var) > 0) then
    mpi_available = .true.
    return
endif
```

## 🚨 故障排除

### 常见问题

#### 1. Docker 镜像未找到
```
Error: Could not find image 'wanniertools-builder-nompi'
```
**解决方案**: 
```bash
docker build -t wanniertools-builder-nompi -f Dockerfile.manylinux-nompi .
```

#### 2. 磁盘空间不足
```
Error: No space left on device
```
**解决方案**:
```bash
# 检查磁盘空间
df -h

# 设置自定义临时目录
export WT_TEMP_DIR="/path/to/large/disk"
```

#### 3. MPI 检测失败
```
You are using 1 CPU cores (expected: 2+ cores)
```
**调试步骤**:
```bash
# 检查 MPI 环境变量
mpirun -np 2 bash -c 'env | grep OMPI'

# 启用调试模式（修改 runtime_mpi.f90）
# 添加 write(*,*) 调试语句
```

#### 4. 构建超时
```
cibuildwheel: Build timed out
```
**解决方案**:
```bash
# 增加构建超时时间
export CIBW_BUILD_TIMEOUT=3600  # 1小时
```

#### 5. 依赖安装失败
**macOS**:
```bash
# 更新 Homebrew
brew update
brew upgrade

# 重新安装依赖
brew reinstall gcc openblas arpack
```

**Windows**:
```bash
# 确保 Visual Studio Build Tools 正确安装
# 重新运行安装程序，选择 C++ 构建工具
```

### 调试模式

启用详细输出：
```bash
# 设置详细构建日志
export CIBW_BUILD_VERBOSITY=3

# 保留构建目录用于调试
export CIBW_BUILD_DEBUG=1
```

### 清理命令

清理构建缓存：
```bash
# 清理 Python 构建缓存
rm -rf build/ dist/ *.egg-info/

# 清理 Docker 缓存
docker system prune -f

# 清理临时目录
rm -rf /tmp/wt_wheel*
```

## 📚 参考资料

### 重要文件说明
- `CROSS_PLATFORM_SUMMARY.md`: 项目完成状态总结
- `scripts/validate_cross_platform.py`: 兼容性验证脚本
- `scripts/cross_platform_info.py`: 平台信息查看
- `src/wannier_tools/_fortran_src/runtime_mpi.f90`: MPI 运行时检测核心模块

### 外部文档
- [cibuildwheel 官方文档](https://cibuildwheel.readthedocs.io/)
- [manylinux 标准](https://github.com/pypa/manylinux)
- [Meson 构建系统](https://mesonbuild.com/)

## 🎯 开发者测试检查清单

### 环境检查
- [ ] Python 3.9+ 已安装
- [ ] Docker 已安装并可用 (Linux)
- [ ] 相关构建工具已安装
- [ ] 足够的磁盘空间 (10GB+)

### 构建检查
- [ ] Docker 镜像构建成功 (Linux)
- [ ] 跨平台兼容性验证通过
- [ ] wheel 包构建成功
- [ ] wheel 包可以安装

### 功能检查
- [ ] 基本导入测试通过
- [ ] 单核运行正常 (1 CPU core)
- [ ] MPI 并行正常 (2+ CPU cores)
- [ ] 不同核心数测试一致

### 交付检查
- [ ] 生成的 wheel 符合 manylinux 标准
- [ ] 在干净环境中安装成功
- [ ] MPI 运行时检测正常工作
- [ ] 跨系统兼容性验证

---

## 🚀 快速开始示例

新开发者快速验证流程：
```bash
# 1. 克隆项目
git clone <repository>
cd wannier_tools_pip

# 2. 构建 Docker 镜像 (Linux only)
docker build -t wanniertools-builder-nompi -f Dockerfile.manylinux-nompi .

# 3. 验证环境
python scripts/validate_cross_platform.py

# 4. 构建测试
python scripts/build/build_with_cibuildwheel.py --platform linux --python cp39 --build-only

# 5. 安装测试
pip install wheelhouse/wannier_tools-*.whl

# 6. 功能测试
python scripts/test_wheel.py
cd wannier_tools/examples/Haldane_model
wt-py && grep "CPU cores" WT.out
```

如果所有步骤都成功，说明环境配置正确！🎉 
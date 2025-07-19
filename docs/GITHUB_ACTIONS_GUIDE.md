# WannierTools GitHub Actions 构建指南

## 🎯 概览

本项目已配置完整的GitHub Actions CI/CD流水线，可以自动为 **Linux、macOS、Windows** 三个平台的 **Python 3.8-3.12** 构建轮子包。

## 📁 项目结构

```
wanniertools_clean/
├── .github/workflows/
│   ├── build_wheels.yml       # 主要的轮子构建流水线
│   └── test_build.yml         # 简单构建测试
├── build_support/
│   └── Dockerfile.manylinux-nompi  # Linux构建环境
├── src/wannier_tools/         # Python源代码
├── examples/                  # 测试示例
├── pyproject.toml            # 项目配置和cibuildwheel设置
├── meson.build               # 构建配置
└── scripts/
    └── test_local_build.py    # 本地测试脚本
```

## 🚀 快速开始

### 1. 本地测试（推荐先执行）

在推送到GitHub之前，建议先进行本地测试：

```bash
# 运行本地测试脚本
python scripts/test_local_build.py

# 如果测试通过，继续下一步
```

### 2. 触发GitHub Actions

GitHub Actions会在以下情况自动触发：

1. **推送到主分支**：
   ```bash
   git add -A
   git commit -m "Update build configuration"
   git push origin main  # 或 master
   ```

2. **创建Pull Request**（仅构建，不发布）

3. **手动触发**：
   - 进入GitHub仓库页面
   - 点击 "Actions" 标签
   - 选择 "Build and Test WannierTools Cross-Platform Wheels"
   - 点击 "Run workflow"

### 3. 监控构建过程

1. 访问: `https://github.com/您的用户名/wannier_tools/actions`
2. 点击最新的workflow运行
3. 查看各个job的状态：
   - `build_wheels` - 在三个平台上构建轮子
   - `test_installation` - 测试轮子安装
   - `test_mpi_functionality` - 测试MPI功能
   - `collect_wheels` - 收集所有轮子

## 🎛️ 构建配置

### 支持的平台和版本

| 平台 | 架构 | Python版本 |
|------|------|------------|
| Linux | x86_64 | 3.8, 3.9, 3.10, 3.11, 3.12 |
| macOS | x86_64, arm64 | 3.8, 3.9, 3.10, 3.11, 3.12 |
| Windows | AMD64 | 3.8, 3.9, 3.10, 3.11, 3.12 |

### 预期输出

成功构建后，将产生约30个轮子文件：
- Linux: 5个轮子 (每个Python版本1个)
- macOS: 10个轮子 (每个Python版本2个架构)
- Windows: 5个轮子 (每个Python版本1个)

## 📦 构建产物

### 下载构建的轮子

1. 进入GitHub Actions运行页面
2. 滚动到底部的 "Artifacts" 部分
3. 下载：
   - `all-wheels` - 所有平台的轮子
   - `wheels-ubuntu-latest` - Linux轮子
   - `wheels-macos-latest` - macOS轮子
   - `wheels-windows-latest` - Windows轮子

### 本地测试轮子

```bash
# 下载并解压轮子
unzip all-wheels.zip

# 测试安装
pip install wannier_tools-2.7.1-cp310-cp310-linux_x86_64.whl

# 验证安装
python -c "import wannier_tools; print(wannier_tools.__version__)"
wt-check-deps
```

## 🔧 故障排除

### 常见问题

1. **构建失败**：
   - 检查依赖是否正确安装
   - 查看specific job的日志
   - 确认Fortran编译器配置

2. **Docker构建失败** (Linux)：
   - 确认`build_support/Dockerfile.manylinux-nompi`存在
   - 检查Docker镜像是否可以构建

3. **macOS依赖问题**：
   - Homebrew依赖可能需要更新
   - 检查`brew install gcc openblas arpack`

4. **Windows编译问题**：
   - Visual Studio环境配置
   - Fortran编译器问题

### 调试技巧

1. **查看详细日志**：
   - 点击失败的job
   - 展开具体的step查看错误信息

2. **本地复现**：
   - 使用相同的环境变量
   - 运行相同的命令

3. **修改配置**：
   - 编辑`.github/workflows/build_wheels.yml`
   - 编辑`pyproject.toml`中的`[tool.cibuildwheel]`部分

## 🚀 发布到PyPI（可选）

当前配置已禁用自动发布。要启用发布：

1. **设置PyPI Token**：
   - 在PyPI创建API token
   - 在GitHub仓库设置中添加Secret: `PYPI_API_TOKEN`

2. **启用发布job**：
   - 编辑`.github/workflows/build_wheels.yml`
   - 取消注释`publish` job

3. **创建版本标签**：
   ```bash
   git tag v2.7.1
   git push origin v2.7.1
   ```

## 📊 性能统计

典型构建时间：
- Linux: ~15-20分钟
- macOS: ~20-25分钟  
- Windows: ~25-30分钟
- 总计: ~60-75分钟

## 🔗 相关链接

- [cibuildwheel文档](https://cibuildwheel.readthedocs.io/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [meson-python文档](https://meson-python.readthedocs.io/)
- [PyPI发布指南](https://packaging.python.org/tutorials/packaging-projects/) 
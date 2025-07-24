# WannierTools

![wanniertools-logo](wt-logo.jpg)

WannierTools 是一个用于研究新型拓扑材料的开源软件包。它提供了一系列强大的工具，用于计算拓扑不变量、表面态、能带结构等。

## ✨ 特点

* **多平台支持**: 兼容 Linux、macOS 和 Windows 操作系统。
* **并行计算**: **目前仅 macOS 支持基于 MPI 的并行计算**，其他平台的并行功能仍在开发中。
* **易于安装**: 提供预编译的 wheel 包，简化了安装过程，无需复杂的编译步骤。
* **功能全面**: 支持 WannierTools 的所有核心功能，满足科研和应用需求。

## 🚀 安装指南

我们推荐通过 PyPI 安装 `wannier-tools`。

```bash
pip install -i https://test.pypi.org/simple/ wannier-tools==0.0.2
```

### 依赖环境

* **操作系统**:

  * **Linux**: CentOS 7 及以上版本
  * **macOS**: 版本 14.6 (Sonoma) 及以上
  * **Windows**: 当前版本功能仍在开发中 (暂不支持运行)
* **Python:** 3.9 - 3.12 版本
* **NumPy:** >= 2.0
* **MPI 运行时:** 无需额外安装，所有平台直接使用内置串行逻辑；仅 macOS 并行时需 `brew install open-mpi`。

## 使用

```bash
# 串行运行（适用于所有平台）
# 默认输入文件为当前目录下的 wt.in
# 如需指定其他输入文件，可使用 -i
wt-py -i wt.in

# 并行运行（仅限 macOS）
# <N> 是并行进程数，例如 4
wt-py -n 4 -i input_file.in
```

## 平台功能支持

| 功能       | Linux   | macOS                       | Windows (开发中) |
| -------- | ------- | --------------------------- | ------------- |
| 串行计算     | ✅       | ✅                           | ❌             |
| MPI 并行计算 | ❌ (开发中) | ✅ (`brew install open-mpi`) | ❌             |

**注意：**

* **所有平台**：直接运行 `wt-py -i wt.in` 即可，无需安装 MPI。
* **macOS 用户**：并行时需先 `brew install open-mpi`。
* **Windows 用户**：当前版本暂不支持运行，后续开发中。

## 许可证

本项目遵循 **GNU General Public License 第3版或更高版本**（GNU GPLv3+）。

## 更多信息

* **源代码地址：** [https://github.com/quanshengwu/wannier\_tools](https://github.com/quanshengwu/wannier_tools)
* **官方文档：** [http://www.wanniertools.com](http://www.wanniertools.com)
* **主页：** [https://www.wanniertools.org](https://www.wanniertools.org)
* **QQ 交流群号：** 709225749

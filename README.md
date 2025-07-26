# WannierTools

![wanniertools-logo](wt-logo.jpg)

WannierTools 是一个用于研究新型拓扑材料的开源软件包。它提供了一系列强大的工具，用于计算拓扑不变量、表面态、能带结构等。

## 📚 资源链接

* **源代码:** [https://github.com/quanshengwu/wannier_tools](https://github.com/quanshengwu/wannier_tools)
* **官方网站:** [https://www.wanniertools.org](https://www.wanniertools.org)
* **官方文档:** [http://www.wanniertools.com](http://www.wanniertools.com)
* **培训手册:** [https://github.com/quanshengwu/WannierToolsTutorials](https://github.com/quanshengwu/WannierToolsTutorials)
* **QQ 交流群:** 709225749

## ✨ 特点

* **多平台支持**: 兼容 Linux、macOS ， Windows 操作系统正在在开发中。
* **并行计算**: **目前仅 macOS 支持基于 MPI 的并行计算**，Linux 和 Windows 平台的并行功能仍在开发中。
* **易于安装**: 提供预编译的 wheel 包，简化了安装过程，无需复杂的编译步骤。
* **功能全面**: 支持 WannierTools 的所有核心功能，满足科研和应用需求。

## 🚀 安装指南

我们推荐通过 pip 安装 `wannier-tools`。

```bash
pip install -i https://test.pypi.org/simple/ wannier-tools
```

### 依赖环境

* **操作系统**:

  * **Linux**: CentOS 7 及以上版本（仅支持串行计算）
  * **macOS**: 版本 14.0 (Sonoma) 及以上，**仅支持 Apple Silicon (ARM) 芯片**（支持串行和并行计算）
  * **Windows**: windows10及以上（暂不支持运行）
* **Python:** 3.9 - 3.12 版本
* **NumPy:**
* **MPI:** 无需额外安装。

## 使用

```bash
# 串行运行（适用于所有平台）
# 默认输入文件为当前目录下的 wt.in
# 如需指定其他输入文件，可使用参数 -i 指定文件
wt-py -i wt.in

# 并行运行（仅限 macOS）
# <N> 是并行进程数，例如 4
wt-py -n 4 -i wt.in
```

## 平台功能支持

| 功能        | Linux      | macOS          | Windows        |
| --------    | ---------- | -------------- | ------------- |
| 串行计算     | ✅         | ✅           | ❌ (开发中)   |
| MPI 并行计算 | ❌ (开发中) | ✅           | ❌ (开发中)   |

**注意：**

* **Linux 用户**：目前仅支持串行计算，无需安装 MPI。
* **macOS 用户**：支持串行和并行计算，无需额外安装 MPI。**注意：仅支持搭载 Apple Silicon (ARM) 芯片的 Mac，不支持 Intel 芯片。**
* **Windows 用户**：当前版本暂不支持运行，功能正在开发中。

## 许可证

本项目遵循 **GNU General Public License 第3版或更高版本**（GNU GPLv3+）。

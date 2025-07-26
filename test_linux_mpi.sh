#!/bin/bash

echo "🔍 测试Linux OpenMPI配置"

# 设置OpenMPI环境变量
export OMPI_MCA_plm=isolated
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export OMPI_MCA_rmaps_base_oversubscribe=yes
export PMIX_MCA_pcompress_base_silence_warning=1

echo "✅ 设置OpenMPI环境变量"

# 测试基本功能
echo "🧪 测试基本导入..."
python -c "import wannier_tools; print(f'✅ wannier_tools {wannier_tools.__version__} 导入成功')"

echo "🧪 测试依赖检查..."
python -c "import wannier_tools.check_deps; wannier_tools.check_deps.main()"

echo "🧪 测试CLI命令..."
wt-check-deps

# 进入测试目录
if [ -d "examples/Haldane_model" ]; then
    cd examples/Haldane_model
    
    echo "🧪 测试单核运行..."
    if wt-py; then
        echo "✅ 单核测试成功"
        if [ -f "WT.out" ] && grep -q "Congratulations!" WT.out; then
            echo "✅ 计算结果正确"
        else
            echo "⚠️ 计算结果可能有问题"
        fi
    else
        echo "❌ 单核测试失败"
    fi
    
    echo "🧪 测试双核并行..."
    rm -f WT.out
    if wt-py -n 2; then
        echo "✅ 双核并行测试成功"
        if [ -f "WT.out" ] && grep -q "Congratulations!" WT.out; then
            echo "✅ 并行计算结果正确"
            cores=$(grep "CPU cores" WT.out | tail -1)
            echo "📊 使用的核心数: $cores"
        else
            echo "⚠️ 并行计算结果可能有问题"
        fi
    else
        echo "❌ 双核并行测试失败"
    fi
else
    echo "❌ 找不到测试目录 examples/Haldane_model"
fi

echo "�� Linux OpenMPI测试完成" 
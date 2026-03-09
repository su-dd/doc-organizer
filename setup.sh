#!/bin/bash

echo "============================================"
echo "  DocOrganizer Pro - 安装脚本"
echo "============================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python3"
    echo "macOS: brew install python3"
    echo "Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi
echo "[✓] Python3 已安装"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未检测到 pip3"
    exit 1
fi

# 检查 Ollama
if ! command -v ollama &> /dev/null; then
    echo "[警告] 未检测到 Ollama"
    echo "请先安装 Ollama:"
    echo "macOS: brew install ollama"
    echo "Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "安装后运行：ollama pull qwen2.5:7b"
    read -p "按回车继续..."
else
    echo "[✓] Ollama 已安装"
fi

# 创建虚拟环境（可选）
read -p "是否创建 Python 虚拟环境？(y/n): " create_venv
if [ "$create_venv" = "y" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[✓] 虚拟环境已创建"
fi

# 安装依赖
echo ""
echo "正在安装 Python 依赖..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo ""
echo "============================================"
echo "  安装完成！"
echo "============================================"
echo ""
echo "下一步:"
echo "1. 如果未安装 Ollama，请根据上面提示安装"
echo "2. 下载 AI 模型：ollama pull qwen2.5:7b"
echo "3. 运行程序：python main.py"
echo ""

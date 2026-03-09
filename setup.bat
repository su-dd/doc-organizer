@echo off
chcp 65001 >nul
echo ============================================
echo   DocOrganizer Pro - 安装脚本
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [✓] Python 已安装

REM 检查 Ollama
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到 Ollama
    echo 请先安装 Ollama: https://ollama.ai/download/windows
    echo 安装后运行：ollama pull qwen2.5:7b
    pause
) else (
    echo [✓] Ollama 已安装
)

REM 安装 Python 依赖
echo.
echo 正在安装 Python 依赖...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ============================================
echo   安装完成！
echo ============================================
echo.
echo 下一步:
echo 1. 如果未安装 Ollama，请访问：https://ollama.ai/download/windows
echo 2. 下载 AI 模型：ollama pull qwen2.5:7b
echo 3. 运行程序：python main.py
echo.
pause

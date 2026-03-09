# DocOrganizer Pro - 快速入门指南

## 5 分钟快速开始

### 第一步：安装依赖（3 分钟）

#### 1. 安装 Python

下载地址：https://www.python.org/downloads/

确保安装时勾选 "Add Python to PATH"

#### 2. 安装 Ollama（本地 AI 引擎）

**Windows**:
```powershell
# 下载安装包
# https://ollama.ai/download/windows
# 运行安装程序
```

**macOS**:
```bash
brew install ollama
```

#### 3. 下载 AI 模型

```bash
# 启动 Ollama 服务
ollama serve

# 在新终端下载模型（约 4GB）
ollama pull qwen2.5:7b
```

#### 4. 安装 Python 依赖

```bash
cd doc-organizer
pip install -r requirements.txt
```

---

### 第二步：运行程序（1 分钟）

#### 图形界面模式

```bash
python main.py
```

#### 命令行模式

```bash
# 扫描文件
python cli.py scan ./documents

# 分类文档
python cli.py classify ./documents --output results.json

# 整理文件（预览）
python cli.py organize ./documents ./organized --results results.json --dry-run

# 整理文件（实际移动）
python cli.py organize ./documents ./organized --results results.json --move
```

---

### 第三步：开始整理（1 分钟）

1. **选择源文件夹** - 点击"浏览"选择杂乱的文件夹
2. **扫描文件** - 点击"🔍 扫描文件"
3. **开始分类** - 点击"🤖 开始分类"（等待 AI 处理）
4. **保存结果** - 点击"💾 保存结果"
5. **整理文件** - 切换到"📁 文件整理"标签页
6. **选择目标文件夹** - 选择整理后的存放位置
7. **开始整理** - 点击"📁 开始整理"

完成！你的文件已经自动分类整理好了 🎉

---

## 常见问题

### Q: 分类准确吗？

A: 使用 qwen2.5:7b 模型，准确率约 85-95%。可以在预览模式检查后再实际操作。

### Q: 处理速度慢怎么办？

A: 
- 使用更小的模型：`qwen2.5:3b`（更快但准确率略低）
- 分批处理：每次处理 50-100 个文件
- 后台运行：分类在后台进行，不影响其他工作

### Q: 支持哪些文件格式？

A: 
- 文本：TXT, MD, PDF, DOC, DOCX
- 代码：PY, JS, CPP, JAVA 等
- 图片：JPG, PNG, GIF（需要 OCR）
- 表格：XLS, XLSX, CSV

### Q: 数据安全吗？

A: **100% 安全**。所有处理都在本地完成：
- 文件不上传云端
- AI 模型本地运行
- 断网也能使用

### Q: 可以自定义分类类别吗？

A: 可以！编辑 `config.yaml` 文件：

```yaml
categories:
  - 合同
  - 发票
  - 报告
  - 我的自定义类别 1
  - 我的自定义类别 2
```

---

## 进阶使用

### 批量处理多个文件夹

```bash
# 创建批处理脚本 process.bat (Windows) 或 process.sh (Mac/Linux)

for folder in */; do
    echo "处理 $folder..."
    python cli.py classify "$folder" --output "$folder/results.json"
    python cli.py organize "$folder" "./organized/$folder" --results "$folder/results.json" --move
done
```

### 只处理特定类型文件

```bash
# 只处理 PDF 和 Word 文档
python cli.py classify ./documents --extensions .pdf .docx .doc --output results.json
```

### 集成到工作流

```python
# 在你的 Python 脚本中使用
from core.classifier import DocumentClassifier
from core.organizer import FileOrganizer

classifier = DocumentClassifier()
organizer = FileOrganizer("./input", "./output")

# 分类
results = classifier.classify("./document.pdf")
print(f"类别：{results['category']}")

# 整理
organizer.organize([results], move=True)
```

---

## 获取帮助

- 📖 完整文档：README.md
- 💼 商业计划：BUSINESS_PLAN.md
- 🐛 问题反馈：[GitHub Issues]
- 💬 讨论交流：[微信群/QQ 群]

---

*祝你使用愉快！* 🦐

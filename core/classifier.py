"""
AI 文档分类引擎
使用本地 Ollama 模型进行文档分类和标签提取
"""

import os
import json
import subprocess
from typing import List, Dict, Tuple
from pathlib import Path


class DocumentClassifier:
    """本地 AI 文档分类器"""
    
    def __init__(self, model: str = "qwen2.5:7b"):
        """
        初始化分类器
        
        Args:
            model: Ollama 模型名称
        """
        self.model = model
        self.categories = [
            "合同",
            "发票", 
            "报告",
            "笔记",
            "邮件",
            "简历",
            "论文",
            "代码",
            "图片",
            "其他"
        ]
    
    def _run_ollama(self, prompt: str) -> str:
        """
        运行本地 Ollama 模型
        
        Args:
            prompt: 输入提示词
            
        Returns:
            模型输出文本
        """
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 分钟超时
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "ERROR: 模型响应超时"
        except FileNotFoundError:
            return "ERROR: 未找到 Ollama，请先安装并运行 ollama serve"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def extract_text(self, file_path: str) -> str:
        """
        从文件中提取文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        try:
            # 文本文件直接读取
            if ext in ['.txt', '.md', '.py', '.js', '.cpp', '.h', '.java', '.json', '.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:5000]  # 限制长度
            
            # PDF 文件（需要额外依赖）
            elif ext == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages[:5]:  # 只读前 5 页
                            text += page.extract_text()
                        return text[:5000]
                except ImportError:
                    return "[PDF 文件 - 需要安装 PyPDF2]"
            
            # Word 文档
            elif ext in ['.docx', '.doc']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    return text[:5000]
                except ImportError:
                    return "[Word 文档 - 需要安装 python-docx]"
            
            else:
                return f"[不支持的文件类型：{ext}]"
                
        except Exception as e:
            return f"[读取失败：{str(e)}]"
    
    def classify(self, file_path: str, content: str = None) -> Dict:
        """
        分类单个文档
        
        Args:
            file_path: 文件路径
            content: 可选的预提取内容
            
        Returns:
            分类结果字典 {category, tags, summary, confidence}
        """
        if content is None:
            content = self.extract_text(file_path)
        
        file_name = os.path.basename(file_path)
        
        # 如果内容太短或无法读取，基于文件名分类
        if len(content) < 50 or content.startswith("[") or content.startswith("ERROR"):
            return self._classify_by_name(file_name)
        
        # 构建分类提示词
        prompt = f"""你是一个专业的文档分类助手。请分析以下文档内容，完成分类任务。

文件名：{file_name}

文档内容（前 5000 字符）：
{content[:3000]}

请按以下 JSON 格式返回结果（只返回 JSON，不要其他文字）：
{{
    "category": "从以下选择：{', '.join(self.categories)}",
    "tags": ["关键词 1", "关键词 2", "关键词 3"],
    "summary": "50 字以内的内容摘要",
    "confidence": 0.0-1.0 之间的置信度
}}

确保返回有效的 JSON 格式。"""

        response = self._run_ollama(prompt)
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON（可能包含在代码块中）
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)
            
            # 验证和修正结果
            if result.get("category") not in self.categories:
                result["category"] = "其他"
            
            if not isinstance(result.get("tags"), list):
                result["tags"] = []
            
            result["confidence"] = float(result.get("confidence", 0.5))
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            # 解析失败，返回基于文件名的分类
            base_result = self._classify_by_name(file_name)
            base_result["summary"] = "AI 解析失败，基于文件名分类"
            base_result["confidence"] = 0.3
            return base_result
    
    def _classify_by_name(self, file_name: str) -> Dict:
        """
        基于文件名进行分类（fallback 方案）
        
        Args:
            file_name: 文件名
            
        Returns:
            分类结果
        """
        name_lower = file_name.lower()
        
        # 基于关键词的分类规则
        rules = [
            (["合同", "协议", "contract", "agreement"], "合同"),
            (["发票", "invoice", "receipt", "账单"], "发票"),
            (["报告", "report", "分析", "总结"], "报告"),
            (["笔记", "note", "memo", "日记"], "笔记"),
            (["邮件", "email", "message"], "邮件"),
            (["简历", "resume", "cv"], "简历"),
            (["论文", "thesis", "paper", "research"], "论文"),
            ([".py", ".js", ".cpp", ".java", "code"], "代码"),
            ([".jpg", ".png", ".gif", ".bmp"], "图片"),
        ]
        
        for keywords, category in rules:
            if any(kw in name_lower for kw in keywords):
                return {
                    "category": category,
                    "tags": [category],
                    "summary": f"基于文件名分类：{file_name}",
                    "confidence": 0.5
                }
        
        return {
            "category": "其他",
            "tags": ["未分类"],
            "summary": f"无法识别的文件：{file_name}",
            "confidence": 0.3
        }
    
    def classify_batch(self, file_paths: List[str], callback=None) -> List[Dict]:
        """
        批量分类文档
        
        Args:
            file_paths: 文件路径列表
            callback: 进度回调函数 (current, total, file_path, result)
            
        Returns:
            分类结果列表
        """
        results = []
        total = len(file_paths)
        
        for i, path in enumerate(file_paths):
            result = self.classify(path)
            result["file_path"] = path
            results.append(result)
            
            if callback:
                callback(i + 1, total, path, result)
        
        return results


if __name__ == "__main__":
    # 测试代码
    classifier = DocumentClassifier()
    
    test_file = "test_document.txt"
    if os.path.exists(test_file):
        result = classifier.classify(test_file)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"测试文件不存在：{test_file}")

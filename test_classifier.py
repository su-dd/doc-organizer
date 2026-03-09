#!/usr/bin/env python3
"""
测试分类器功能
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.classifier import DocumentClassifier
from core.organizer import FileOrganizer


def test_classify_by_name():
    """测试基于文件名的分类"""
    print("=" * 60)
    print("测试：基于文件名的分类")
    print("=" * 60)
    
    classifier = DocumentClassifier()
    
    test_cases = [
        "购房合同.pdf",
        "2024 年发票.pdf",
        "年度工作总结报告.docx",
        "学习笔记.md",
        "简历_张三.pdf",
        "毕业论文.pdf",
        "main.py",
        "photo.jpg",
        "random_file.txt"
    ]
    
    for filename in test_cases:
        result = classifier._classify_by_name(filename)
        print(f"{filename:30} → {result['category']:10} (置信度：{result['confidence']:.2f})")
    
    print()


def test_extract_text():
    """测试文本提取"""
    print("=" * 60)
    print("测试：文本提取")
    print("=" * 60)
    
    # 创建测试文件
    test_content = """
    这是一个测试文档。
    
    合同编号：HT2024001
    甲方：某某公司
    乙方：张三
    
    本合同规定了一些条款和条件...
    """
    
    test_file = "test_contract.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    classifier = DocumentClassifier()
    extracted = classifier.extract_text(test_file)
    
    print(f"原始长度：{len(test_content)}")
    print(f"提取长度：{len(extracted)}")
    print(f"提取内容:\n{extracted[:200]}...")
    
    # 清理
    os.remove(test_file)
    print("\n✓ 测试文件已清理")
    print()


def test_organizer():
    """测试文件整理器"""
    print("=" * 60)
    print("测试：文件整理器")
    print("=" * 60)
    
    # 创建测试文件夹
    test_source = "./test_documents"
    test_target = "./test_organized"
    
    os.makedirs(test_source, exist_ok=True)
    
    # 创建测试文件
    test_files = [
        ("合同 1.txt", "合同"),
        ("发票 1.txt", "发票"),
        ("笔记 1.txt", "笔记"),
        ("报告 1.txt", "报告"),
    ]
    
    for filename, _ in test_files:
        with open(os.path.join(test_source, filename), 'w', encoding='utf-8') as f:
            f.write(f"这是{filename}的内容")
    
    print(f"✓ 创建 {len(test_files)} 个测试文件")
    
    # 测试扫描
    organizer = FileOrganizer(test_source, test_target)
    files = organizer.scan_folder(test_source)
    print(f"✓ 扫描到 {len(files)} 个文件")
    
    # 测试文件夹结构
    structure = organizer.get_folder_structure()
    print(f"✓ 文件夹结构：{structure['name']} ({len(structure['children'])} 个子项)")
    
    # 清理
    import shutil
    shutil.rmtree(test_source)
    if os.path.exists(test_target):
        shutil.rmtree(test_target)
    
    print("✓ 测试文件已清理")
    print()


def main():
    """运行所有测试"""
    print("\n🧪 DocOrganizer Pro - 分类器测试\n")
    
    test_classify_by_name()
    test_extract_text()
    test_organizer()
    
    print("=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 确保 Ollama 已安装并运行：ollama serve")
    print("2. 下载 AI 模型：ollama pull qwen2.5:7b")
    print("3. 运行完整测试：python cli.py classify ./your_documents")
    print()


if __name__ == "__main__":
    main()

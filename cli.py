#!/usr/bin/env python3
"""
DocOrganizer Pro - 命令行界面
本地 AI 文档智能整理工具
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.classifier import DocumentClassifier
from core.organizer import FileOrganizer


def print_progress(current: int, total: int, file_path: str, result: dict):
    """打印进度"""
    percent = (current / total) * 100
    category = result.get("category", "?")
    confidence = result.get("confidence", 0)
    filename = os.path.basename(file_path)
    
    # 进度条
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    print(f"\r[{bar}] {percent:.1f}% | {filename} → {category} ({confidence:.2f})", end="", flush=True)
    
    if current == total:
        print()  # 换行


def cmd_classify(args):
    """分类命令"""
    print(f"🤖 DocOrganizer Pro - 文档分类")
    print(f"=" * 50)
    
    # 初始化分类器
    classifier = DocumentClassifier(model=args.model)
    print(f"✓ 使用模型：{args.model}")
    
    # 扫描文件
    organizer = FileOrganizer(args.source, args.target)
    files = organizer.scan_folder(args.source, extensions=args.extensions)
    
    if not files:
        print("❌ 未找到任何文件")
        return 1
    
    print(f"✓ 找到 {len(files)} 个文件")
    print()
    
    # 批量分类
    print("开始分类...")
    start_time = datetime.now()
    
    results = classifier.classify_batch(files, callback=print_progress)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 统计结果
    categories = {}
    for r in results:
        cat = r.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1
    
    print()
    print(f"✓ 分类完成！耗时：{duration:.1f}秒")
    print()
    print("📊 分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 个文件")
    
    # 保存结果
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 结果已保存：{args.output}")
    
    return 0


def cmd_organize(args):
    """整理命令"""
    print(f"📁 DocOrganizer Pro - 文件整理")
    print(f"=" * 50)
    
    # 检查分类结果文件
    if not os.path.exists(args.results):
        print(f"❌ 分类结果文件不存在：{args.results}")
        return 1
    
    with open(args.results, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"✓ 加载 {len(results)} 个分类结果")
    
    # 初始化整理器
    organizer = FileOrganizer(args.source, args.target)
    
    # 执行整理
    action = "移动" if args.move else "复制"
    print(f"✓ 操作模式：{action}")
    
    if args.dry_run:
        print(f"✓ 预览模式（不会实际操作）")
    
    print()
    print("开始整理...")
    
    stats = organizer.organize(
        results,
        move=args.move,
        dry_run=args.dry_run
    )
    
    print()
    print(f"✓ 整理完成！")
    print()
    print("📊 整理统计:")
    print(f"  总计：{stats['total']} 个文件")
    print(f"  成功：{stats['success']} 个")
    print(f"  失败：{stats['failed']} 个")
    print(f"  跳过：{stats['skipped']} 个")
    
    if args.dry_run:
        print()
        print("预览目标位置:")
        for detail in stats['details'][:10]:  # 只显示前 10 个
            if detail['status'] == 'preview':
                print(f"  {os.path.basename(detail['file'])} → {detail['target']}")
        if len(stats['details']) > 10:
            print(f"  ... 还有 {len(stats['details']) - 10} 个")
    
    return 0


def cmd_scan(args):
    """扫描命令"""
    print(f"🔍 DocOrganizer Pro - 文件扫描")
    print(f"=" * 50)
    
    organizer = FileOrganizer(args.source, args.target)
    files = organizer.scan_folder(args.source, extensions=args.extensions)
    
    print(f"✓ 扫描路径：{args.source}")
    print(f"✓ 找到 {len(files)} 个文件")
    
    if args.verbose:
        print()
        print("文件列表:")
        for f in files:
            size = os.path.getsize(f)
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
            print(f"  {f} ({size_str})")
    
    # 保存文件列表
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
        print(f"✓ 列表已保存：{args.output}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="DocOrganizer Pro - 本地 AI 文档智能整理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 扫描文件夹
  python cli.py scan ./documents
  
  # 分类文档
  python cli.py classify ./documents --output results.json
  
  # 整理文件（预览模式）
  python cli.py organize ./documents ./organized --results results.json --dry-run
  
  # 整理文件（实际移动）
  python cli.py organize ./documents ./organized --results results.json --move
        """
    )
    
    parser.add_argument(
        "--model", 
        default="qwen2.5:7b",
        help="Ollama 模型名称 (默认：qwen2.5:7b)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="扫描文件夹")
    scan_parser.add_argument("source", help="源文件夹路径")
    scan_parser.add_argument("--extensions", "-e", nargs="+", help="文件扩展名过滤")
    scan_parser.add_argument("--output", "-o", help="输出文件路径")
    scan_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    # classify 命令
    classify_parser = subparsers.add_parser("classify", help="分类文档")
    classify_parser.add_argument("source", help="源文件夹路径")
    classify_parser.add_argument("--extensions", "-e", nargs="+", help="文件扩展名过滤")
    classify_parser.add_argument("--output", "-o", help="输出分类结果文件")
    classify_parser.add_argument("--target", "-t", default="./organized", help="目标文件夹")
    
    # organize 命令
    organize_parser = subparsers.add_parser("organize", help="整理文件")
    organize_parser.add_argument("source", help="源文件夹路径")
    organize_parser.add_argument("target", help="目标文件夹路径")
    organize_parser.add_argument("--results", "-r", required=True, help="分类结果文件")
    organize_parser.add_argument("--move", "-m", action="store_true", help="移动文件（默认复制）")
    organize_parser.add_argument("--dry-run", "-n", action="store_true", help="预览模式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行命令
    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "classify":
        return cmd_classify(args)
    elif args.command == "organize":
        return cmd_organize(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

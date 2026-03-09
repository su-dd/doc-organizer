"""
文件整理引擎
根据分类结果自动整理文件到目标文件夹
"""

import os
import shutil
from typing import List, Dict
from pathlib import Path
from datetime import datetime


class FileOrganizer:
    """文件整理器"""
    
    def __init__(self, source_folder: str, target_folder: str):
        """
        初始化整理器
        
        Args:
            source_folder: 源文件夹路径
            target_folder: 目标文件夹路径
        """
        self.source = Path(source_folder)
        self.target = Path(target_folder)
        
        # 确保目标文件夹存在
        self.target.mkdir(parents=True, exist_ok=True)
    
    def organize(self, classification_results: List[Dict], 
                 move: bool = False,
                 dry_run: bool = False) -> Dict:
        """
        根据分类结果整理文件
        
        Args:
            classification_results: 分类结果列表
            move: True=移动文件，False=复制文件
            dry_run: True=仅预览，不实际操作
            
        Returns:
            整理统计信息
        """
        stats = {
            "total": len(classification_results),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        for result in classification_results:
            file_path = result.get("file_path")
            category = result.get("category", "其他")
            
            if not file_path or not os.path.exists(file_path):
                stats["failed"] += 1
                stats["details"].append({
                    "file": file_path,
                    "status": "failed",
                    "reason": "文件不存在"
                })
                continue
            
            # 创建目标文件夹
            category_folder = self.target / category
            if not dry_run:
                category_folder.mkdir(parents=True, exist_ok=True)
            
            # 生成目标文件名（避免重名）
            original_name = os.path.basename(file_path)
            target_name = self._generate_unique_filename(category_folder, original_name)
            target_path = category_folder / target_name
            
            # 执行操作
            try:
                if dry_run:
                    action = "移动" if move else "复制"
                    stats["details"].append({
                        "file": file_path,
                        "status": "preview",
                        "target": str(target_path),
                        "action": action
                    })
                    stats["success"] += 1
                else:
                    if move:
                        shutil.move(file_path, target_path)
                        action = "移动"
                    else:
                        shutil.copy2(file_path, target_path)
                        action = "复制"
                    
                    stats["success"] += 1
                    stats["details"].append({
                        "file": file_path,
                        "status": "success",
                        "target": str(target_path),
                        "action": action
                    })
                    
            except Exception as e:
                stats["failed"] += 1
                stats["details"].append({
                    "file": file_path,
                    "status": "failed",
                    "reason": str(e)
                })
        
        return stats
    
    def _generate_unique_filename(self, folder: Path, filename: str) -> str:
        """
        生成唯一的文件名（避免覆盖）
        
        Args:
            folder: 目标文件夹
            filename: 原始文件名
            
        Returns:
            唯一的文件名
        """
        base, ext = os.path.splitext(filename)
        target_path = folder / filename
        
        if not target_path.exists():
            return filename
        
        # 文件已存在，添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{base}_{timestamp}{ext}"
        
        counter = 1
        while (folder / new_filename).exists():
            new_filename = f"{base}_{timestamp}_{counter}{ext}"
            counter += 1
        
        return new_filename
    
    def scan_folder(self, folder: str = None, 
                    extensions: List[str] = None) -> List[str]:
        """
        扫描文件夹获取文件列表
        
        Args:
            folder: 要扫描的文件夹（默认使用 source）
            extensions: 要扫描的文件扩展名列表（None=全部）
            
        Returns:
            文件路径列表
        """
        folder_path = Path(folder) if folder else self.source
        
        if not folder_path.exists():
            return []
        
        files = []
        
        # 递归扫描所有文件
        for item in folder_path.rglob("*"):
            if item.is_file():
                # 如果指定了扩展名，进行过滤
                if extensions:
                    if item.suffix.lower() in extensions:
                        files.append(str(item))
                else:
                    files.append(str(item))
        
        return files
    
    def get_folder_structure(self, folder: Path = None) -> Dict:
        """
        获取文件夹结构（用于显示）
        
        Args:
            folder: 文件夹路径
            
        Returns:
            文件夹结构字典
        """
        folder_path = folder or self.source
        
        if not folder_path.exists():
            return {"name": folder_path.name, "type": "not_found", "children": []}
        
        result = {
            "name": folder_path.name,
            "type": "folder",
            "path": str(folder_path),
            "children": []
        }
        
        # 获取直接子项（不递归）
        try:
            items = list(folder_path.iterdir())
            for item in sorted(items, key=lambda x: (x.is_file(), x.name)):
                if item.is_file():
                    result["children"].append({
                        "name": item.name,
                        "type": "file",
                        "size": item.stat().st_size,
                        "path": str(item)
                    })
                else:
                    result["children"].append({
                        "name": item.name,
                        "type": "folder",
                        "path": str(item)
                    })
        except PermissionError:
            pass
        
        return result
    
    def create_category_folders(self, categories: List[str]) -> List[str]:
        """
        创建分类文件夹
        
        Args:
            categories: 分类名称列表
            
        Returns:
            创建的文件夹路径列表
        """
        created = []
        
        for category in categories:
            folder_path = self.target / category
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                created.append(str(folder_path))
        
        return created


if __name__ == "__main__":
    # 测试代码
    organizer = FileOrganizer("./documents", "./organized")
    
    # 扫描文件夹
    files = organizer.scan_folder()
    print(f"找到 {len(files)} 个文件")
    
    # 预览文件夹结构
    structure = organizer.get_folder_structure()
    print(f"文件夹结构：{structure['name']}")

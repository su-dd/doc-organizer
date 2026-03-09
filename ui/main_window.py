"""
DocOrganizer Pro - 图形界面
使用 PyQt5 构建的桌面应用
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QCheckBox,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.classifier import DocumentClassifier
from core.organizer import FileOrganizer


class ClassificationWorker(QThread):
    """分类工作线程"""
    progress = pyqtSignal(int, int, str, dict)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, files, model):
        super().__init__()
        self.files = files
        self.model = model
    
    def run(self):
        try:
            classifier = DocumentClassifier(model=self.model)
            results = classifier.classify_batch(
                self.files, 
                callback=lambda c, t, f, r: self.progress.emit(c, t, f, r)
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class OrganizationWorker(QThread):
    """整理工作线程"""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, organizer, results, move, dry_run):
        super().__init__()
        self.organizer = organizer
        self.results = results
        self.move = move
        self.dry_run = dry_run
    
    def run(self):
        try:
            stats = self.organizer.organize(
                self.results,
                move=self.move,
                dry_run=self.dry_run
            )
            self.finished.emit(stats)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.results = []
        self.files = []
        
        self.init_ui()
        self.init_workers()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("DocOrganizer Pro - 本地 AI 文档智能整理")
        self.setMinimumSize(900, 700)
        
        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 标题
        title = QLabel("🤖 DocOrganizer Pro")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("本地 AI 文档智能整理工具 - 完全离线，隐私安全")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # 选项卡
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 标签页 1: 分类
        classify_tab = self.create_classify_tab()
        tabs.addTab(classify_tab, "📝 文档分类")
        
        # 标签页 2: 整理
        organize_tab = self.create_organize_tab()
        tabs.addTab(organize_tab, "📁 文件整理")
        
        # 标签页 3: 设置
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "⚙️ 设置")
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_classify_tab(self):
        """创建分类标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 源文件夹选择
        source_group = QGroupBox("1. 选择源文件夹")
        source_layout = QHBoxLayout()
        
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("选择要整理的文件夹...")
        source_layout.addWidget(self.source_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(browse_btn)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # 文件列表
        list_group = QGroupBox("2. 文件列表")
        list_layout = QVBoxLayout()
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["文件名", "大小", "类型"])
        self.file_tree.setMaximumHeight(200)
        list_layout.addWidget(self.file_tree)
        
        scan_btn = QPushButton("🔍 扫描文件")
        scan_btn.clicked.connect(self.scan_files)
        list_layout.addWidget(scan_btn)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 分类进度
        progress_group = QGroupBox("3. 分类进度")
        progress_layout = QVBoxLayout()
        
        self.classify_progress = QProgressBar()
        self.classify_progress.setFormat("%p% - %v/%m")
        progress_layout.addWidget(self.classify_progress)
        
        self.classify_log = QTextEdit()
        self.classify_log.setReadOnly(True)
        self.classify_log.setMaximumHeight(150)
        progress_layout.addWidget(self.classify_log)
        
        self.classify_btn = QPushButton("🤖 开始分类")
        self.classify_btn.clicked.connect(self.start_classification)
        self.classify_btn.setEnabled(False)
        progress_layout.addWidget(self.classify_btn)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 结果统计
        stats_group = QGroupBox("4. 分类统计")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("暂无数据")
        stats_layout.addWidget(self.stats_label)
        
        save_btn = QPushButton("💾 保存结果")
        save_btn.clicked.connect(self.save_results)
        save_btn.setEnabled(False)
        self.save_results_btn = save_btn
        stats_layout.addWidget(save_btn)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        return widget
    
    def create_organize_tab(self):
        """创建整理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 加载分类结果
        load_group = QGroupBox("1. 加载分类结果")
        load_layout = QHBoxLayout()
        
        self.results_edit = QLineEdit()
        self.results_edit.setPlaceholderText("选择分类结果 JSON 文件...")
        load_layout.addWidget(self.results_edit)
        
        load_btn = QPushButton("浏览...")
        load_btn.clicked.connect(self.browse_results)
        load_layout.addWidget(load_btn)
        
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # 目标文件夹
        target_group = QGroupBox("2. 选择目标文件夹")
        target_layout = QHBoxLayout()
        
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("选择整理后的目标文件夹...")
        target_layout.addWidget(self.target_edit)
        
        target_browse_btn = QPushButton("浏览...")
        target_browse_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(target_browse_btn)
        
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # 选项
        options_group = QGroupBox("3. 选项")
        options_layout = QFormLayout()
        
        self.move_check = QCheckBox("移动文件（不勾选则为复制）")
        options_layout.addRow("", self.move_check)
        
        self.dry_run_check = QCheckBox("预览模式（不实际操作）")
        self.dry_run_check.setChecked(True)
        options_layout.addRow("", self.dry_run_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 执行整理
        action_group = QGroupBox("4. 执行整理")
        action_layout = QVBoxLayout()
        
        self.organize_progress = QProgressBar()
        action_layout.addWidget(self.organize_progress)
        
        self.organize_log = QTextEdit()
        self.organize_log.setReadOnly(True)
        self.organize_log.setMaximumHeight(150)
        action_layout.addWidget(self.organize_log)
        
        self.organize_btn = QPushButton("📁 开始整理")
        self.organize_btn.clicked.connect(self.start_organization)
        self.organize_btn.setEnabled(False)
        action_layout.addWidget(self.organize_btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        return widget
    
    def create_settings_tab(self):
        """创建设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI 模型设置
        model_group = QGroupBox("AI 模型")
        model_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "qwen2.5:7b",
            "qwen2.5:3b",
            "gemma2:7b",
            "llama3.1:8b",
            "mistral:7b"
        ])
        model_layout.addRow("模型:", self.model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # 文件类型过滤
        filter_group = QGroupBox("文件类型过滤")
        filter_layout = QFormLayout()
        
        self.filter_edit = QLineEdit(".pdf,.docx,.txt,.md,.jpg,.png")
        filter_layout.addRow("扩展名:", self.filter_edit)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        layout.addStretch()
        
        # 关于
        about_group = QGroupBox("关于")
        about_layout = QVBoxLayout()
        
        about_label = QLabel(
            "<b>DocOrganizer Pro v1.0</b><br><br>"
            "本地 AI 文档智能整理工具<br>"
            "完全离线运行，保护您的隐私<br><br>"
            "定价：<br>"
            "• 个人版：299 元（永久）<br>"
            "• 专业版：29 元/月<br>"
            "• 企业版：1999 元/年"
        )
        about_layout.addWidget(about_label)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        return widget
    
    def init_workers(self):
        """初始化工作线程"""
        self.classify_worker = None
        self.organize_worker = None
    
    def browse_source(self):
        """浏览源文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if folder:
            self.source_edit.setText(folder)
    
    def browse_results(self):
        """浏览分类结果文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择分类结果", "", "JSON Files (*.json)"
        )
        if file_path:
            self.results_edit.setText(file_path)
    
    def browse_target(self):
        """浏览目标文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if folder:
            self.target_edit.setText(folder)
    
    def scan_files(self):
        """扫描文件"""
        source = self.source_edit.text()
        if not source or not os.path.exists(source):
            QMessageBox.warning(self, "警告", "请选择有效的源文件夹")
            return
        
        # 获取扩展名过滤
        filter_text = self.filter_edit.text()
        extensions = None
        if filter_text:
            extensions = [ext.strip() for ext in filter_text.split(",")]
        
        # 扫描
        organizer = FileOrganizer(source, "./temp")
        self.files = organizer.scan_folder(source, extensions)
        
        # 显示在树形控件中
        self.file_tree.clear()
        for file_path in self.files[:100]:  # 只显示前 100 个
            name = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
            ext = os.path.splitext(name)[1]
            
            item = QTreeWidgetItem([name, size_str, ext])
            self.file_tree.addTopLevelItem(item)
        
        if len(self.files) > 100:
            item = QTreeWidgetItem([f"... 还有 {len(self.files) - 100} 个文件", "", ""])
            self.file_tree.addTopLevelItem(item)
        
        self.classify_btn.setEnabled(len(self.files) > 0)
        self.statusBar().showMessage(f"找到 {len(self.files)} 个文件")
    
    def start_classification(self):
        """开始分类"""
        if not self.files:
            QMessageBox.warning(self, "警告", "请先扫描文件")
            return
        
        model = self.model_combo.currentText()
        
        # 创建工作线程
        self.classify_worker = ClassificationWorker(self.files, model)
        self.classify_worker.progress.connect(self.on_classify_progress)
        self.classify_worker.finished.connect(self.on_classify_finished)
        self.classify_worker.error.connect(self.on_classify_error)
        
        self.classify_btn.setEnabled(False)
        self.classify_log.clear()
        self.classify_progress.setValue(0)
        self.classify_progress.setMaximum(len(self.files))
        
        self.classify_worker.start()
        self.statusBar().showMessage("正在分类...")
    
    def on_classify_progress(self, current, total, file_path, result):
        """分类进度更新"""
        self.classify_progress.setValue(current)
        
        filename = os.path.basename(file_path)
        category = result.get("category", "?")
        confidence = result.get("confidence", 0)
        
        self.classify_log.append(f"[{current}/{total}] {filename} → {category} ({confidence:.2f})")
    
    def on_classify_finished(self, results):
        """分类完成"""
        self.results = results
        self.classify_btn.setEnabled(True)
        self.save_results_btn.setEnabled(True)
        
        # 统计
        categories = {}
        for r in results:
            cat = r.get("category", "其他")
            categories[cat] = categories.get(cat, 0) + 1
        
        stats_text = "分类统计:\n"
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            stats_text += f"  {cat}: {count} 个文件\n"
        
        self.stats_label.setText(stats_text)
        self.statusBar().showMessage(f"分类完成！共 {len(results)} 个文件")
    
    def on_classify_error(self, error):
        """分类错误"""
        self.classify_btn.setEnabled(True)
        QMessageBox.critical(self, "错误", f"分类失败：{error}")
        self.statusBar().showMessage("分类失败")
    
    def save_results(self):
        """保存结果"""
        if not self.results:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存分类结果", "classification_results.json", "JSON Files (*.json)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", f"结果已保存:\n{file_path}")
    
    def start_organization(self):
        """开始整理"""
        results_file = self.results_edit.text()
        target = self.target_edit.text()
        source = self.source_edit.text()
        
        if not results_file or not os.path.exists(results_file):
            QMessageBox.warning(self, "警告", "请选择分类结果文件")
            return
        
        if not target:
            QMessageBox.warning(self, "警告", "请选择目标文件夹")
            return
        
        # 加载结果
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 创建整理器
        organizer = FileOrganizer(source, target)
        
        move = self.move_check.isChecked()
        dry_run = self.dry_run_check.isChecked()
        
        # 创建工作线程
        self.organize_worker = OrganizationWorker(organizer, results, move, dry_run)
        self.organize_worker.progress.connect(self.on_organize_progress)
        self.organize_worker.finished.connect(self.on_organize_finished)
        self.organize_worker.error.connect(self.on_organize_error)
        
        self.organize_btn.setEnabled(False)
        self.organize_log.clear()
        self.organize_progress.setValue(0)
        self.organize_progress.setMaximum(len(results))
        
        self.organize_worker.start()
        
        mode = "预览" if dry_run else ("移动" if move else "复制")
        self.statusBar().showMessage(f"正在{mode}文件...")
    
    def on_organize_progress(self, current, total, message):
        """整理进度更新"""
        self.organize_progress.setValue(current)
        self.organize_log.append(f"[{current}/{total}] {message}")
    
    def on_organize_finished(self, stats):
        """整理完成"""
        self.organize_btn.setEnabled(True)
        
        summary = (
            f"整理完成!\n\n"
            f"总计：{stats['total']} 个文件\n"
            f"成功：{stats['success']} 个\n"
            f"失败：{stats['failed']} 个\n"
            f"跳过：{stats['skipped']} 个"
        )
        
        QMessageBox.information(self, "完成", summary)
        self.statusBar().showMessage("整理完成")
    
    def on_organize_error(self, error):
        """整理错误"""
        self.organize_btn.setEnabled(True)
        QMessageBox.critical(self, "错误", f"整理失败：{error}")
        self.statusBar().showMessage("整理失败")


def main():
    app = QApplication(sys.argv)
    
    # 设置样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

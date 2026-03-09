#!/usr/bin/env python3
"""
DocOrganizer Pro - 主入口
图形界面启动文件
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import main

if __name__ == "__main__":
    main()

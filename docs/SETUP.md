# GitHub Pages 部署指南

## ✅ 文件已上传

网站文件已上传到 `docs/` 文件夹：
- `index.html` - 主页
- `styles.css` - 样式表

---

## 🚀 启用 GitHub Pages（3 步）

### 第 1 步：打开仓库设置
访问：https://github.com/su-dd/doc-organizer/settings/pages

### 第 2 步：配置 Pages
1. 找到 **Pages** 菜单（左侧）
2. **Source** 选择：`Deploy from a branch`
3. **Branch** 选择：`main` 
4. **Folder** 选择：`/docs`
5. 点击 **Save**

### 第 3 步：等待部署
- GitHub 会自动构建（约 1-2 分钟）
- 部署成功后会显示访问链接
- 链接格式：`https://su-dd.github.io/doc-organizer/`

---

## 📊 网站预览

### 包含的板块：
1. **Hero 区域** - 产品名称 + 标语 + 下载按钮
2. **功能特性** - 6 个特性卡片（本地运行、AI 分类、自动摘要等）
3. **快速开始** - 3 步安装教程
4. **版本对比** - 开源版 vs 专业版 vs 企业版
5. **页脚** - GitHub 链接 + 版权信息

### 设计特点：
- 🎨 科技蓝配色方案
- 📱 响应式设计（支持手机/平板/桌面）
- ⚡ 纯 HTML + CSS（无框架依赖）
- 🎯 转化导向（突出下载按钮）

---

## 🔗 访问地址

启用后访问：
```
https://su-dd.github.io/doc-organizer/
```

---

## 📝 后续更新

修改网站后：
```bash
# 1. 修改 docs/ 下的文件
# 2. 提交
git add docs/
git commit -m "Update website"
# 3. 推送（自动部署）
git push origin main
```

GitHub 会自动重新部署（约 1 分钟）。

---

## 🎨 自定义

### 修改配色
编辑 `docs/styles.css` 中的颜色值：
```css
/* 主色调 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* 文字颜色 */
color: #667eea;
```

### 修改内容
编辑 `docs/index.html` 中的文本。

### 添加分析
在 `</head>` 前添加：
```html
<!-- Google Analytics / 百度统计 -->
```

---

## 💡 进阶优化

### 1. 添加 favicon
```bash
# 将 favicon.ico 放到 docs/ 文件夹
git add docs/favicon.ico
git commit -m "Add favicon"
git push
```

### 2. 添加社交媒体卡片
在 `index.html` 的 `<head>` 中添加：
```html
<meta property="og:title" content="DocOrganizer Pro">
<meta property="og:description" content="本地 AI 文档智能整理工具">
<meta property="og:image" content="og-image.png">
```

### 3. 自定义域名
1. 在仓库设置中添加 `CNAME` 文件
2. 内容：`yourdomain.com`
3. 在域名提供商处配置 CNAME 记录

---

*部署时间：2026-03-09*

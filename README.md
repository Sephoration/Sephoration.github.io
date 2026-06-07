# 🌐 Sephoration's Blog

基于 Hugo 和 FixIt 主题的个人博客网站。

## ✨ 博客特性

- **主题**: FixIt
- **框架**: Hugo
- **部署**: GitHub Pages
- **支持**: 多语言、搜索、评论系统

## 📂 项目结构

```
Sephoration.github.io/
├── content/           # 博客内容
│   └── posts/         # 文章
├── themes/            # 主题目录
│   └── FixIt/         # FixIt 主题
├── assets/            # 资源文件
├── .github/           # GitHub Actions 配置
└── hugo.toml          # Hugo 配置
```

## 🚀 本地运行

### 安装 Hugo
```bash
# 下载 Hugo Extended 版本
# https://gohugo.io/getting-started/installing/
```

### 启动本地服务器
```bash
hugo server -D
```

访问 http://localhost:1313 查看博客。

### 生成静态文件
```bash
hugo
```

生成的文件在 `public/` 目录。

## 📝 写文章

### 创建新文章
```bash
hugo new posts/your-post-title.md
```

### 文章前置配置
```markdown
---
title: "文章标题"
date: 2024-01-01T00:00:00+08:00
draft: false
tags: ["标签1", "标签2"]
categories: ["分类"]
---

文章内容...
```

## 🎨 主题配置

主题配置在 `hugo.toml` 文件中。

详细配置请参考 [FixIt 文档](https://fixit.lruihao.cn/)。

## 🔧 部署

使用 GitHub Actions 自动部署到 GitHub Pages。

配置见 `.github/workflows/hugo.yml`。

## 📚 相关链接

- [Hugo 官网](https://gohugo.io/)
- [FixIt 主题](https://github.com/hugo-fixit/FixIt)
- [GitHub Pages](https://pages.github.com/)

---

**© 2024 Sephoration**

# Sephoration Blog

> Stay hungry, stay foolish.

基于 **Hugo** 的个人技术博客，使用 **FixIt v1** 主题，主题组件以 Git 子模块 + 本地组件方式管理。

- **构建**：Hugo v0.168.0 (extended) + Dart Sass
- **部署**：GitHub Pages + GitHub Actions（push 到 `main` 自动构建部署）
- **文章**：`content/posts/`，page bundle 方式（图片与 `index.md` 同目录，相对路径引用）
- **发布**：源目录写作 + 博客发布器自动搬运（`scripts/publish.py` + `tools/publisher/`），见「日常发布流程」

---

## 挂载的插件

| 组件 | 挂载方式 | 来源 | 作用 |
|------|---------|------|------|
| **FixIt** | Git 子模块 | `hugo-fixit/FixIt` (main) | 主主题：全部功能、样式、短代码 |
| **component-projects** | Git 子模块 | `hugo-fixit/component-projects` | `{{< gh-repo-card >}}` 仓库卡片、项目页 |
| **cmpt-markmap** | Git 子模块 | `hugo-fixit/cmpt-markmap` | ` ```markmap ` 思维导图渲染 |
| **cmpt-sephoration** | 本地组件 | `themes/cmpt-sephoration` | 自定义样式（阅读进度条、返回顶部、Header 特效）+ i18n 覆盖 |

组件通过 `[module.mounts]` 挂载：主题 `_shortcodes` → 短代码、`_partials` → partials、`_markup` → 渲染钩子，本地文件优先。

---

## 写一篇文章

在 `content/posts/` 下新建目录，放入 `index.md` 和图片，顶部写：

```
---
title: "文章标题"
date: 2026-08-12
---

图片用相对路径引用：![](图片名.jpg)
```

> 推荐用下面「日常发布流程」的源目录方式写作，工具会自动完成以上落地工作。

---

## 日常发布流程（博客发布器）

写作和图片统一放在**源目录**，不用手动碰 `content/posts/`：

- **主目录**（默认 `C:\Users\Eoooo\Desktop\博客大文件夹`）：正式文章，按「分类/章节文件夹」组织
- **收件箱**（默认 `C:\Users\Eoooo\Desktop\博客收件箱`）：随手写的单篇笔记可直接丢在根下，在 Obsidian 里写完拖过来即可

**源目录约定**

- 两种写法都支持：**一章一个 `.md`** 直接放在分类文件夹里（Obsidian 平铺，推荐），或**一章一个文件夹**（文件夹里只放一个同名 `.md`）
- 文章在博客里的路径 = 相对源目录的路径（去掉 `.md`），例如 `知识库/操作系统/2、进程管理.md` → `/posts/知识库/操作系统/2、进程管理/`
- 图片放哪都行，按「md 同目录 → 源根目录 → 全树唯一文件名」顺序找；Obsidian 的 `%20` 编码链接也能识别，带空格的图片名会自动用 `<...>` 包裹链接
- 两个源里路径撞车时按「来源目录|路径」区分（界面会标「重名」）；选目录时禁止选根目录/盘符第一层，避免扫描整个文件系统

**发布方式**

1. 双击桌面「博客发布器」文件夹里的 **打开发布器.bat** → 浏览器打开管理界面（http://localhost:8765）：勾选发布 / 全部发布 / 干跑预览，可开自动监听；鼠标悬停「文章 / 源文件」可看修改、创建、首发时间（同名文件据此区分）
2. 桌面「打开博客预览.bat」一键本地预览（http://localhost:1313），「关闭博客预览.bat」关掉
3. 在 opencode 里：`/draft` 本地预览（不提交）、`/publish` 正式发布上线

**工具自动完成**：搬运文章与图片到 `content/posts/`（md 统一为 `index.md`、图片链接改写为同目录裸文件名、同名自动加后缀）；空图注自动用文件名填充；缺 `date` 自动补「首次发布日」（之后固定不变）；发布前跑全量 Hugo 构建验证，失败自动回滚；通过后自动 `git commit` + `push`，GitHub Actions 自动部署。

**安全规则**：目标目录已存在且不是工具发布的（比如手动放进去的），默认拒绝覆盖，确认要替换才勾选「强制覆盖」（命令行 `--force`）；工具不会删除任何图片文件。

**命令行等价**：`python3 scripts/publish.py`（发布全部待发布/有更新）、`--scan`（只看状态）、`--dry-run`（干跑预览）、`--no-git`（只本地落地预览）、`--select 路径…`（指定篇目，重名时用「来源|路径」）、`--source 目录…`（临时指定源目录）。

---

## 发布器配置与接口（预留）

配置文件 `~/.config/blog-publisher/config.json`（首次运行自动生成，界面「目录设置」也会写这里）：

| 键 | 默认 | 用途 |
|----|------|------|
| `source_roots` | 主目录 + 收件箱 | 源目录列表，第一个是主目录，其余是收件箱 |
| `port` / `preview_port` | 8765 / 1313 | 发布器界面端口 / 本地预览端口 |
| `watch_interval_sec` | 15 | 界面自动监听刷新间隔（秒） |
| `branch` | main | 推送分支 |
| `hugo_bin` / `hugo_args` | 空 | 自定义 hugo 可执行文件与构建参数 |
| `commit_message_template` | `post: {verb}{title}` | 提交信息模板（{verb}=新增/更新） |

发布清单 `~/.config/blog-publisher/manifest.json` 记录每篇的哈希、原始文件、创建/修改/首发时间、commit 等，用于判断「未发布 / 有更新 / 已发布」，删掉后重新运行会按现状重建。

本地 HTTP 接口（`tools/publisher/app.py`）：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/scan` | GET | 全量状态（文章列表、错误、未引用图片、计数） |
| `/api/config` | GET/POST | 读取 / 保存目录设置（Windows 路径自动转换） |
| `/api/dirs` | GET | 浏览目录（给设置界面用） |
| `/api/publish` | POST | 触发发布任务（mode: all / select / dry，可 force） |
| `/api/log` | GET | 增量拉取任务日志与结果 |

---

## 博客功能

| 类别 | 功能 | 状态 | 说明 |
|------|------|------|------|
| 写作与渲染 | Markdown 扩展 | ✅ | 高亮、上下标、删除线、脚注、任务列表等（见下方速查） |
| 写作与渲染 | 数学公式 | ✅ | KaTeX：块级 `$$...$$` / `\[...\]`，行内 `$...$` / `\(...\)` |
| 写作与渲染 | Mermaid 图表 | ✅ | ` ```mermaid `，手绘风格（`look=handDrawn`），支持暗色 |
| 写作与渲染 | ECharts 图表 | ✅ | ` ```echarts ` |
| 写作与渲染 | JSON 查看器 | ✅ | ` ```json ` 代码块自动格式化渲染 |
| 写作与渲染 | 代码块工具箱 | ✅ | classic 模式：复制、行号切换、折行切换、全屏 |
| 写作与渲染 | Ruby 注音 | ✅ | `[中文]^(拼音)` |
| 写作与渲染 | 分数 | ✅ | `[1]/[2]` |
| 写作与渲染 | FontAwesome 图标 | ✅ | `:(fa-solid fa-user):` |
| 写作与渲染 | 提示框 | ✅ | `{{< admonition type >}}`（13 种）或 `> [!NOTE]` |
| 写作与渲染 | 内容加密 | ✅ | `{{< fixit-encryptor >}}` |
| 写作与渲染 | 折叠区域 | ✅ | `{{< details title >}}` |
| 写作与渲染 | 标签页 | ✅ | `{{< tabs >}}{{< tab >}}` |
| 写作与渲染 | 时间线 | ✅ | `{{< timeline >}}` / ` ```timeline ` |
| 写作与渲染 | 文件树 | ✅ | `{{< file-tree >}}` / ` ```file-tree ` |
| 写作与渲染 | 思维导图 | ✅ | ` ```markmap `（cmpt-markmap 组件） |
| 写作与渲染 | 链接卡片 | ✅ | `{{< link >}}` |
| 写作与渲染 | 增强图片 | ✅ | `{{< image >}}` |
| 写作与渲染 | 居中引用 | ✅ | `{{< center-quote >}}` |
| 写作与渲染 | 版本号标签 | ✅ | `{{< version >}}` |
| 写作与渲染 | GitHub Gist | ✅ | `{{< gist user repo >}}` |
| 写作与渲染 | 打印支持 | ✅ | 打印时自动展开提示框/代码块/折叠区域 |
| 布局与导航 | 个人资料首页 | ✅ | 头像 + 座右铭 + GitHub 链接，TypeIt 打字机动画 |
| 布局与导航 | 主页文章列表 | ❌ | `[params.home.posts] enable=false`，可开启 |
| 布局与导航 | 归档页 | ✅ | `/posts/` 展示全部文章 |
| 布局与导航 | 项目页 | ✅ | `/projects/`（GitHub 仓库卡片） |
| 布局与导航 | 关于页 | ✅ | `/about/` |
| 布局与导航 | 离线页 | ✅ | `/offline/` |
| 布局与导航 | RSS | ✅ | 首页 + 分区订阅 |
| 布局与导航 | 分类/标签/合集页 | ✅ | `/categories/` `/tags/`（taxonomies 已配置） |
| 布局与导航 | 目录 TOC | ✅ | 右侧自动目录，支持 2-6 级标题 |
| 布局与导航 | 面包屑导航 | ✅ | 页面顶部路径导航 |
| 布局与导航 | 最近更新 | ✅ | 归档/列表页显示 7 天内更新的文章 |
| 布局与导航 | 文字统计 | ✅ | 文章字数和阅读时间 |
| 布局与导航 | 最后修改时间 | ✅ | 文章显示 `show_lastmod=true` 的最后更新日期 |
| 布局与导航 | 标签云 | ✅ | 侧边栏标签云（`[params.tag_cloud] enable=true`） |
| 布局与导航 | 文章链接工具栏 | ✅ | 每篇文章提供 Markdown 原文/源码/编辑/报告链接（VS Code） |
| 布局与导航 | 文章内上下篇导航 | ❌ | `[params.navigation] in_section=false`，可开启 |
| 布局与导航 | 合集列表 | ❌ | `collection_list=false`，侧边栏显示合集目录 |
| 布局与导航 | 合集导航 | ❌ | `collection_navigation=false`，文末上一章/下一章 |
| 布局与导航 | 标题编号 | ❌ | `[params.heading.number] enable=false`，可开启 |
| 媒体与嵌入 | 图片灯箱 | ✅ | `lightgallery=force`，所有图片点击放大 |
| 媒体与嵌入 | 图片懒加载 | ✅ | 所有内容图片 `loading=lazy` |
| 媒体与嵌入 | 音频播放器 | ✅ | `{{< aplayer >}}` / `{{< audio >}}` |
| 媒体与嵌入 | 音乐播放列表 | ✅ | `{{< music >}}`（APlayer + MetingJS） |
| 媒体与嵌入 | 视频嵌入 | ✅ | `{{< bilibili BV >}}` / `{{< douyin id >}}` |
| 媒体与嵌入 | 帖子嵌入 | ✅ | `{{< bluesky user >}}` / `{{< spotify id >}}` |
| 媒体与嵌入 | 互动地图 | ❌ | Mapbox 需配置 access token |
| 媒体与嵌入 | GitHub 角标 | ❌ | `[params.github_corner] enable=false`，可开启 |
| 性能与体验 | 客户端搜索 | ✅ | Fuse.js 全文搜索（`type=fuse`），首页生成 `search.json` |
| 性能与体验 | 即时页面 | ✅ | instant.page 悬停链接预加载 |
| 性能与体验 | 阅读进度条 | ✅ | 顶部绿色进度条 |
| 性能与体验 | 返回顶部 | ✅ | 右下角返回顶部按钮 |
| 性能与体验 | 暗色模式 | ✅ | 默认暗色（`default_theme=dark`），支持手动切换 |
| 性能与体验 | 主题配色定制 | ✅ | `[params.appearance]` 全套颜色变量，可自定义主题色 |
| 性能与体验 | 全局 tooltip | ✅ | `tooltip=true`，元素悬停提示 |
| 性能与体验 | 图片优化 | ✅ | `optimise=true`：自动生成 webp + srcset（800/1200/1600w），灯箱仍看原图 |
| 性能与体验 | PWA | ❌ | 未启用 |
| 性能与体验 | 自动书签 | ❌ | `auto_bookmark=false` |
| 性能与体验 | 到期提醒 | ❌ | `[params.expiration_reminder] enable=false` |
| 性能与体验 | Pace 加载进度条 | ❌ | `[params.pace] enable=false`，可开启 |
| 性能与体验 | Twemoji 表情 | ❌ | `twemoji=false`，可开启 Twitter 表情渲染 |
| 性能与体验 | Gravatar 头像 | ❌ | `[params.gravatar] enable=false` |
| 性能与体验 | 中英文自动间距 | ❌ | `[params.pangu] enable=false`，可开启 |
| 数据与合规 | Cookie 同意 | ✅ | 弹出横幅 |
| 数据与合规 | 页脚版权 | ✅ | 自 2025 年起，隐藏 Hugo/FixIt 水印 |
| 数据与合规 | 评论系统 | ❌ | 全部禁用（artalk/twikoo/giscus 等 11 种可配置） |
| 数据与合规 | 社交分享 | ❌ | `[params.share] enable=false` |
| 数据与合规 | 相关文章 | ❌ | `[params.related] enable=false` |
| 数据与合规 | 网站统计 | ❌ | Busuanzi 禁用 |
| 数据与合规 | 网站分析 | ❌ | 全部禁用（Google/Fathom/Baidu 等） |
| 数据与合规 | 打赏 | ❌ | `[params.reward] enable=false` |
| 数据与合规 | 水印 | ❌ | `[params.watermark] enable=false` |
| 数据与合规 | PostChat AI 聊天 | ❌ | `[params.post_chat] enable=false`，可开启 |
| 数据与合规 | AI 文章摘要 | ❌ | `[params.post_summary] enable=false`，可开启 |
| 数据与合规 | 播客订阅 | ❌ | `[params.podcast] enable=false` |
| 数据与合规 | 自定义搜索引擎 | ❌ | `[params.cse] engine=""`，可接入 Google/Bing |
| 数据与合规 | 外链守卫 | ❌ | `[params.link.guard] enable=false`，外链中转确认 |
| 数据与合规 | 网站验证 | ❌ | `[params.verification]` 未配置（Google/Bing 等） |

---

## Markdown 扩展

| 语法 | 效果 |
|------|------|
| `==高亮==` | 高亮标记 |
| `++插入++` | 插入/下划线 |
| `~下标~` | 下标 |
| `^上标^` | 上标 |
| `~~删除~~` | 删除线 |
| `[^1]` / `[^1]: 内容` | 脚注 |
| `- [x]` 已完成 | 任务列表 |
| `- 定义项` + `: 描述` | 定义列表 |
| `\| 列1 \| 列2 \|` | 表格 |
| `https://...` | URL 自动链接 |
| `{#id .class}` | 块级 HTML 属性 |
| `{title="xxx"}` | 标题级 HTML 属性 |
| 原始 HTML | 允许（`unsafe=true`） |
| `> [!NOTE]` | 提示框（alert 语法） |

### 围栏代码块

| 语法 | 渲染效果 |
|------|----------|
| ` ```echarts ` | ECharts 图表 |
| ` ```file-tree ` | 文件目录树 |
| ` ```mermaid ` | Mermaid 图表 |
| ` ```timeline ` | 时间线 |
| ` ```json ` | JSON 格式化查看器 |
| ` ```markmap ` | Markmap 思维导图 |
| ` ```toggle ` | 折叠切换块 |

---

© 2025 - 2026 Eric Sephoration

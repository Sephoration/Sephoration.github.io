# Sephoration.github.io

Code. Create. Explore.

写代码，创造，探索。

一个 Qt 学习者，用 C++ 构建桌面应用，用文字记录技术之路。

---

### 关于这个站点

极简、干净、不打扰。

Lighthouse 性能测试：**97** 分。可访问性 **96**，最佳实践 **100**，SEO **92**。

白天它安静地待着，到了黑夜，底部会浮现一句：

> Stay hungry, stay foolish.

### 技术栈

本站基于 [Hugo](https://gohugo.io/) 构建，所有主题及组件均以 **Git 子模块** 方式管理：

| 组件 | 仓库 | 位置 |
|------|------|------|
| **cmpt-sephoration**（自定义） | — | `themes/cmpt-sephoration` |
| **FixIt** 主题 | `github.com/hugo-fixit/FixIt` | `themes/FixIt` |
| **component-projects** | `github.com/hugo-fixit/component-projects` | `themes/component-projects` |
| **cmpt-markmap** | `github.com/hugo-fixit/cmpt-markmap` | `themes/cmpt-markmap` |

FixIt 的设计理念是**能配置的尽量走 `hugo.toml`** — 颜色、字体、Logo、开关选项都在 `[params.*]` 里控制。只有配置覆盖不了的东西（布局结构改动、自定义 CSS 样式），才需要在 `cmpt-sephoration` 里写模板或 SCSS。

所有自定义样式、模板覆写均放在 `themes/cmpt-sephoration/` 中，**不直接修改 FixIt 主题源码**。根目录下不保留 `layouts/` 和 `assets/`，所有覆写统一在组件内管理。

**主题加载优先级（左侧优先）：**

```
cmpt-sephoration  →  FixIt  →  component-projects  →  cmpt-markmap
(你的自定义)         (主题核心)    (GitHub 项目组件)        (思维导图组件)
```

### 已启用功能一览

#### 核心功能

| 功能 | 配置值 | 说明 |
|------|--------|------|
| 搜索 | `enable=true`, type=fuse | 客户端全文搜索（Fuse.js），首页生成 `search.json` |
| 图片灯箱 | `lightgallery=force` | 所有图片点击放大 |
| 数学公式 | KaTeX | 块级 `$$...$$` / `\[...\]`，行内 `$...$` / `\(...\)` |
| Mermaid 图表 | `look=handDrawn` | 手绘风格，支持暗色主题 |
| 代码块工具箱 | classic 模式 | 复制、行号切换、折行切换、全屏 |
| JSON 查看器 | `enable=true` | 代码块中 JSON 自动格式化渲染 |
| 阅读进度条 | `enable=true` | 顶部绿色进度条 |
| 即时页面 | `instantPage=true` | 鼠标悬停链接时预加载 |
| 返回顶部 | `enable=true` | 右下角返回顶部按钮 |
| TypeIt 打字机 | 首页标题 + 副标题 | 动态打字动画 |

#### 文章页功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 作者头像 | ✅ | 文章顶栏显示 |
| 文字统计 | ✅ | 文章字数和阅读时间 |
| 目录（TOC） | ✅ | 右侧自动目录，支持2-6级标题 |
| 面包屑导航 | ✅ | 页面顶部路径导航 |
| 代码块复制 | ✅ | 一键复制代码 |
| 行号切换 | ✅ | 可收起行号 |
| 折行切换 | ✅ | 切换长代码是否折行 |
| 最近更新 | ✅ | 归档/列表页显示近期更新的文章 |
| Ruby 注音 | ✅ | `{% ruby 中文\|拼音 %}` |
| 分数 | ✅ | `{% fraction 1/2 %}` |
| FontAwesome | ✅ | `{% icon fa-solid fa-user %}` |
| 到期提醒 | ❌ | 未启用 |
| 自动书签 | ❌ | 未启用 |
| 相关文章 | ❌ | 未启用 |
| 社交分享 | ❌ | 未启用 |

#### 互动与媒体

| 功能 | 状态 | 说明 |
|------|------|------|
| APlayer 音频播放器 | ✅ | 首页播放音频 |
| Bilibili 视频嵌入 | ✅ | `{{< bilibili BV >}}` |
| 抖音视频嵌入 | ✅ | `{{< douyin id >}}` |
| Bluesky 帖子嵌入 | ✅ | `{{< bluesky user >}}` |
| Spotify 嵌入 | ✅ | `{{< spotify id >}}` |
| 音乐播放列表 | ✅ | `{{< music ... >}}`（APlayer + MetingJS） |
| Mapbox 地图 | ❌ | 未配置 access token |

#### 页面布局

| 功能 | 状态 | 说明 |
|------|------|------|
| 个人资料首页 | ✅ | 头像 + 座右铭 + GitHub 链接 |
| 主页文章列表 | ❌ | 首页不显示文章列表 |
| 归档页 | ✅ | `/posts/` 展示全部文章 |
| 项目页 | ✅ | `/projects/`（GitHub 仓库卡片） |
| 关于页 | ✅ | `/about/` |
| 离线页 | ✅ | `/offline/` |
| RSS | ✅ | 首页 + 分区订阅 |
| 分类/标签页 | ❌ | `disableKinds` 禁用 |

#### 其他

| 功能 | 状态 | 说明 |
|------|------|------|
| Cookie 同意 | ✅ | 弹出横幅 |
| 页脚版权 | ✅ | 自 2025 年起，隐藏 Hugo/FixIt 水印 |
| 暗色模式 | ✅ | `defaultTheme=auto` 跟随系统 |
| 面包屑导航 | ✅ | 分隔符 `/` |
| PWA | ❌ | 未启用 |
| 评论系统 | ❌ | 全部禁用 |
| 网站统计 | ❌ | Busuanzi 禁用 |
| 网站分析 | ❌ | 全部禁用 |

---

### 可用短代码

#### FixIt 内置短代码（20+）

| 短代码 | 说明 |
|--------|------|
| `{{< admonition type title >}}` | 提示框（note/tip/important/warning/caution 等） |
| `{{< aplayer >}}...{{< /aplayer >}}` | 音频播放器容器 |
| `{{< audio name url cover >}}` | 单曲音频 |
| `{{< bilibili BV >}}` | 嵌入 B 站视频 |
| `{{< bluesky user >}}` | 嵌入 Bluesky 帖子 |
| `{{< center-quote >}}` | 居中引用 |
| `{{< details title >}}...{{< /details >}}` | 折叠区域 |
| `{{< douyin id >}}` | 嵌入抖音视频 |
| `{{< echarts >}}...{{< /echarts >}}` | ECharts 图表 |
| `{{< file-tree >}}...{{< /file-tree >}}` | 文件目录树 |
| `{{< fixit-encryptor >}}...{{< /fixit-encryptor >}}` | 内容加密 |
| `{{< gist user repo >}}` | 嵌入 GitHub Gist |
| `{{< image src >}}` | 增强图片 |
| `{{< link href title >}}` | 链接卡片 |
| `{{< mapbox lng lat >}}` | 互动地图（需 token） |
| `{{< mermaid >}}...{{< /mermaid >}}` | Mermaid 图表 |
| `{{< music id >}}` | 音乐播放列表 |
| `{{< spotify id >}}` | 嵌入 Spotify |
| `{{< tabs >}}{{< tab title >}}...{{< /tab >}}{{< /tabs >}}` | 标签页 |
| `{{< timeline >}}...{{< /timeline >}}` | 时间线 |
| `{{< typeit >}}...{{< /typeit >}}` | 打字机动画 |
| `{{< version >}}` | 版本号标签 |

#### 渲染钩子（围栏代码块语法）

| 语法 | 渲染效果 |
|------|----------|
| ` ```echarts ` | ECharts 图表 |
| ` ```file-tree ` | 文件目录树 |
| ` ```mermaid ` | Mermaid 图表 |
| ` ```timeline ` | 时间线 |
| ` ```json ` | JSON 格式化查看器 |
| ` ```markmap ` | Markmap 思维导图 |
| ` ```toggle ` | 折叠切换块 |
| `> [!NOTE]` | 提示框（alert 语法） |

#### 挂载组件短代码

| 短代码 | 来源 | 说明 |
|--------|------|------|
| `{{< gh-repo-card user/repo >}}` | component-projects | GitHub 仓库卡片 |
| `{{< gh-repo-card-container >}}...{{< /gh-repo-card-container >}}` | component-projects | 仓库卡片网格 |
| `{{< markmap >}}...{{< /markmap >}}` | cmpt-markmap | 思维导图 |

---

### Markdown 扩展（Goldmark）

#### 基础扩展

| 语法 | 效果 |
|------|------|
| `- 定义项` + `: 描述` | 定义列表 |
| `[^1]` / `[^1]: 内容` | 脚注 |
| `https://...` | URL 自动链接 |
| `\| 列1 \| 列2 \|` | 表格 |
| `- [x] 已完成` | 任务列表 |

#### 额外扩展（Hugo v0.123+）

| 语法 | 效果 |
|------|------|
| `++下划线++` | 插入/下划线 |
| `==高亮==` | 高亮标记 |
| `~下标~` | 下标 |
| `^上标^` | 上标 |
| `~~删除~~` | ❌ 未启用 |

#### 属性与安全

| 特性 | 说明 |
|------|------|
| `{#id .class}` | 块级 HTML 属性 |
| `{title="xxx"}` | 标题级 HTML 属性 |
| 原始 HTML | ✅ 允许（`unsafe=true`） |

---

### FixIt 功能说明文档

| 文件 | 内容 |
|------|------|
| `FixIt功能说明/00-配置-FixIt.md` | 站点配置说明 |
| `FixIt功能说明/01-时间线-Timeline.md` | Timeline 短代码与扩展语法 |
| `FixIt功能说明/02-图表-ECharts.md` | ECharts 扩展语法 |
| `FixIt功能说明/03-图表-Mermaid.md` | Mermaid 扩展语法 |
| `FixIt功能说明/04-文件树-FileTree.md` | FileTree 短代码 |
| `FixIt功能说明/05-音频播放器-APlayer.md` | APlayer + audio 短代码 |
| `FixIt功能说明/06-标签页-Tabs.md` | Tabs 短代码 |
| `FixIt功能说明/07-嵌入B站视频-Bilibili.md` | Bilibili 短代码 |
| `FixIt功能说明/08-音乐播放器-Music.md` | Music 播放列表短代码 |
| `FixIt功能说明/09-互动地图-Mapbox.md` | Mapbox 短代码 |
| `FixIt功能说明/10-短代码-ECharts.md` | ECharts 短代码模式 |
| `FixIt功能说明/11-短代码-Mermaid.md` | Mermaid 短代码模式 |
| `FixIt功能说明/12-折叠内容-Details.md` | Details 折叠区域 |
| `FixIt功能说明/13-链接卡片-Link.md` | Link 卡片短代码 |
| `FixIt功能说明/14-增强图片-Image.md` | Image 增强图片 |
| `FixIt功能说明/15-文章加密-FixItEncryptor.md` | 内容加密 |
| `FixIt功能说明/16-提示框-Admonition.md` | 13 种提示框 |
| `FixIt功能说明/17-打字动画-TypeIt.md` | 打字机动画 |
| `FixIt功能说明/18-JSON查看器-JSONViewer.md` | JSON 交互查看器 |
| `FixIt功能说明/19-Bluesky嵌入-Bluesky.md` | Bluesky 帖子 |
| `FixIt功能说明/20-抖音嵌入-Douyin.md` | 抖音视频 |
| `FixIt功能说明/21-GitHubGist-Gist.md` | GitHub Gist |
| `FixIt功能说明/22-Spotify嵌入-Spotify.md` | Spotify 音乐 |

---

### 写一篇文章

在 `content/posts/` 下新建 `.md` 文件，顶部写：

```
---
title: "文章标题"
date: 2026-06-29T00:00:00+08:00
draft: false
weight: 1
---
```

> **注意：** `date` 必须带时区（`+08:00`），否则 Hugo 可能不渲染今天的文章。见 [#关于日期格式](###关于日期格式)。

### 关于日期格式

文章 `date` 字段**必须带时区后缀**（如 `+08:00`，表示东八区），格式为 `2006-01-02T15:04:05+08:00`。

**正确：**
```yaml
date: 2026-06-29T00:00:00+08:00
```

**错误（会出 bug）：**
```yaml
date: 2026-06-29
```

不带时区的日期会被 Hugo 解析为 `UTC 00:00`。如果系统时间在 UTC 凌晨附近，Hugo 会认为文章"未到发布时间"而跳过渲染，导致 404。

如果不想写时间，可以用一个确定过去的日期：
```yaml
date: 2026-06-28
```

图片放在 `static/images/`，文章里用 `![](/images/xxx.png)` 引用。

### 关于最近更新

文章只写 `date` 字段，不写 `lastmod`。修改文章后 `git push`，Hugo 会自动读取 git 提交时间作为最后修改时间，文章会出现在"最近更新"列表中，7 天后自动消失。

---

### 站点配置摘要

- **Hugo 版本**: v0.162.1+extended
- **语言**: zh-CN，时区 Asia/Shanghai
- **菜单**: 文章 `/archives/` · 个人介绍 `/about/`

---

© 2025 - 2026 Eric Sephoration

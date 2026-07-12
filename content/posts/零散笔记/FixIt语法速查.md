---
title: "FixIt 语法速查"
date: 2026-07-12
tags: ["FixIt 功能说明", "零散笔记"]
---

## Admonition 提示框

```
{{</* admonition type=tip title="标题" open=true */>}}
提示内容
{{</* /admonition */>}}
```
或 Alert 语法：
```
> [!TIP]
> 提示内容
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| type | note/abstract/info/todo/tip/success/question/warning/failure/danger/bug/example/quote | note |
| title | 标题 | type 值 |
| open | 默认展开 | true |

## Image 增强图片

```
{{</* image src="/images/photo.jpg" alt="描述" caption="标题" width="" height="" linked=true */>}}
```

| 参数 | 说明 |
|------|------|
| src (1st) | 路径（必填） |
| alt (2nd) | 替代文本 |
| caption (3rd) | 图标题 |
| title | lightgallery 放大 |
| linked | 可点击 | true |
| loading | lazy |

## Tabs 标签页

```
{{</* tabs defaultTab=0 type="underline" placement="top" */>}}
{{%/* tab title="标签1" */%}}内容1{{%/* /tab */%}}
{{%/* tab title="标签2" */%}}内容2{{%/* /tab */%}}
{{</* /tabs */>}}
```

| 参数 | 可选值 |
|------|--------|
| type | underline / pill / card / segment |
| placement | top / bottom / left / right |
| defaultTab | 0 ~ n-1 |

## Details 折叠内容

```
{{</* details "标题" open=false */>}}
折叠内容
{{</* /details */>}}
```

| 参数 | 说明 |
|------|------|
| summary (1st) | 标题 |
| open (2nd) | 默认展开 |
| name | 同组互斥 |

## Link 链接卡片

```
{{</* link "https://url" "显示文本" "提示" card=false card-icon="" */>}}
```

| 参数 | 说明 |
|------|------|
| href (1st) | URL（必填） |
| content (2nd) | 显示文本 |
| title (3rd) | 鼠标悬停提示 |
| card (4th) | 卡片样式 |
| card-icon (5th) | 图标 CSS class |

## Timeline 时间线

````markdown
```timeline {reverse=false animation=false placement=bottom}
events:
  - timestamp: 2024-07-11
    content: 创建成功
    type: primary
    color: "#0CBD87"
    size: large
    node: dot
```
````

## TypeIt 打字动画

```
{{</* typeit speed=100 cursorChar="|" loop=false */>}}
打字内容
{{</* /typeit */>}}
```

| 参数 | 说明 |
|------|------|
| code | 代码语言（语法高亮） |
| group | 同组顺序播放 |
| speed | 打字速度 ms | 100 |
| loop | 循环 |

```
{{</* typeit code=java */>}}
public class Hello {}
{{</* /typeit */>}}
```

## Bilibili 视频

```
{{</* bilibili BV19S411c7Wu */>}}
{{</* bilibili BV1kt411k7Rq 3 */>}}     // 多P指定集数
{{</* bilibili id=BV19S411c7Wu p=1 autoplay=false muted=false danmaku=true */>}}
```

## Douyin 抖音

```
{{</* douyin 7388149561765760266 */>}}
{{</* douyin id=7388149561765760266 */>}}
```

## Bluesky

```
{{</* bluesky link="https://bsky.app/profile/user/post/postid" */>}}
```

## Spotify

```
{{</* spotify type=artist id=74ASZWbe4lXaubB36ztrGX */>}}
{{</* spotify artist 74ASZWbe4lXaubB36ztrGX */>}}
```

## GitHub Gist

```
{{</* gist 用户名 gistID */>}}
{{</* gist 用户名 gistID 文件名.js */>}}
```

## ECharts 图表

推荐用代码块语法：
````markdown
```echarts
{
  "title": { "text": "标题", "left": "center" },
  "xAxis": { "type": "category", "data": ["Mon","Tue","Wed"] },
  "yAxis": { "type": "value" },
  "series": [{ "data": [820, 932, 901], "type": "line" }]
}
```
````
或用 shortcode：
```
{{</* echarts */>}}
JSON / YAML / TOML 格式 option
{{</* /echarts */>}}
```

## Mermaid 图表

推荐用代码块语法：
````markdown
```mermaid
graph LR;
    A[Start] --> B{Decision}
    B -->|Yes| C[Result 1]
```
````
或用 shortcode：
```
{{</* mermaid */>}}
// mermaid code
{{</* /mermaid */>}}
```

Mermaid 类型：流程图 (graph)、时序图 (sequenceDiagram)、类图 (classDiagram)、状态图 (stateDiagram-v2)、ER 图 (erDiagram)、甘特图 (gantt)、用户旅程图 (journey)。

## FileTree 文件树

```
{{</* file-tree */>}}
[files]
[files."src"]
[files."src/components".Header]
content = "Header.tsx"
{{</* /file-tree */>}}
```
支持 TOML / YAML / JSON 格式。

## APlayer 音频播放器

```
{{</* aplayer fixed=false mini=false autoplay=false theme="#b7daff" loop="all" order="list" volume=0.7 mutex=true */>}}
  {{</* audio name="歌曲名" artist="艺术家" url="/music/song.mp3" cover="/images/cover.png" */>}}
{{</* /aplayer */>}}
```

## Music 音乐播放器

```
{{</* music url="/music/song.mp3" name=SongName artist=Artist cover="/images/cover.webp" */>}}
{{</* music auto="https://music.163.com/#/playlist?id=60198" */>}}
{{</* music server="netease" type="song" id="1868553" */>}}
```

server: netease / tencent / kugou / xiami / baidu
type: song / playlist / album / search / artist

## Mapbox 互动地图

```
{{</* mapbox lng=113.953277 lat=22.559102 zoom=11 */>}}
{{</* mapbox 113.953277 22.559102 11 */>}}
```

需要 `hugo.toml` 中配置 `[params.mapbox] accessToken`。

## JSON 查看器

````markdown
```json {expandDepth=2, copyable=true, sort=false, boxed=true}
{ "key": "value" }
```
````

## FixIt Encryptor 内容加密

```
{{</* fixit-encryptor password="1234" message="提示文字" */>}}
加密内容
{{</* /fixit-encryptor */>}}
```

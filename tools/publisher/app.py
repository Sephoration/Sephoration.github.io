#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
PUBLISH_PY = os.path.join(SCRIPTS_DIR, "publish.py")

sys.path.insert(0, SCRIPTS_DIR)
import publish as pipeline

JOB = {"running": False, "lines": [], "result": None, "exit": None, "started": None}
JOB_LOCK = threading.Lock()

STATUS_TEXT = {
    "unpublished": "未发布",
    "published": "已发布",
    "updated": "有更新",
    "error": "有错误",
    "blocked": "目录被占",
}

SCAN_LOCK = threading.Lock()
SCAN_CACHE = {"payload": None}


def scan_payload():
    if not SCAN_LOCK.acquire(blocking=False):
        cached = SCAN_CACHE["payload"]
        if cached:
            out = dict(cached)
            out["scanning"] = True
            return out
        return {"ok": False, "error": "正在扫描，请稍候刷新…"}
    try:
        cfg = pipeline.load_config()
        data = pipeline.do_scan(cfg)
        roots = [pipeline.norm_path(r) for r in (cfg.get("source_roots") or [])]
        main = roots[0] if roots else ""
        inboxes = roots[1:]
        data["main_root"] = main
        data["inbox_roots"] = inboxes
        for a in data.get("articles", []):
            a["status_text"] = STATUS_TEXT.get(a["status"], a["status"])
            a["inbox"] = bool(inboxes) and pipeline.norm_path(a["root"]) in inboxes
        SCAN_CACHE["payload"] = data
        return data
    finally:
        SCAN_LOCK.release()


def start_job(mode, select, force):
    with JOB_LOCK:
        if JOB["running"]:
            return False, "已有发布任务在运行"
        cmd = [sys.executable, PUBLISH_PY]
        if mode == "dry":
            cmd.append("--dry-run")
        if force:
            cmd.append("--force")
        if mode == "all":
            pass
        elif select:
            cmd += ["--select"] + list(select)
        elif mode != "dry":
            return False, "没有选中任何文章"
        JOB.update({"running": True, "lines": [], "result": None, "exit": None,
                    "started": time.strftime("%H:%M:%S"), "cmd": " ".join(cmd[2:])})

    def run():
        try:
            proc = subprocess.Popen(cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in proc.stdout:
                line = line.rstrip("\n")
                if line.startswith("##RESULT## "):
                    try:
                        JOB["result"] = json.loads(line[len("##RESULT## "):])
                    except Exception:
                        JOB["lines"].append(line)
                    continue
                JOB["lines"].append(line)
            proc.wait()
            with JOB_LOCK:
                JOB["exit"] = proc.returncode
        except Exception as e:
            JOB["lines"].append("启动失败：%s" % e)
            with JOB_LOCK:
                JOB["exit"] = -1
        finally:
            with JOB_LOCK:
                JOB["running"] = False

    threading.Thread(target=run, daemon=True).start()
    return True, "已开始"


def list_dirs(path):
    path = pipeline.norm_path(path) if path else ""
    if not path:
        for cand in ("/mnt/c/Users/Eoooo/Desktop", "/mnt/c/Users/Eoooo", os.path.expanduser("~")):
            if os.path.isdir(cand):
                path = cand
                break
    if not os.path.isdir(path):
        return {"ok": False, "error": "目录不存在：%s" % path}
    dirs = []
    try:
        for name in sorted(os.listdir(path)):
            if name.startswith(".") or name.startswith("~"):
                continue
            full = os.path.join(path, name)
            if os.path.isdir(full):
                try:
                    md_count = len([f for f in os.listdir(full) if pipeline.is_md(f)])
                except Exception:
                    md_count = 0
                dirs.append({"name": name, "path": full, "md_count": md_count})
    except PermissionError:
        return {"ok": False, "error": "没有权限读取：%s" % path}
    parent = os.path.dirname(path.rstrip("/")) or "/"
    return {"ok": True, "path": path, "parent": parent, "dirs": dirs}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, text):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            cfg = pipeline.load_config()
            page = PAGE.replace("__PREVIEW_PORT__", str(cfg.get("preview_port", 1313)))
            page = page.replace("__WATCH_MS__", str(int(cfg.get("watch_interval_sec", 5)) * 1000))
            self._html(page)
        elif u.path == "/api/config":
            self._json(pipeline.load_config())
        elif u.path == "/api/scan":
            try:
                self._json(scan_payload())
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, 500)
        elif u.path == "/api/dirs":
            self._json(list_dirs(q.get("path", [""])[0]))
        elif u.path == "/api/log":
            after = int(q.get("after", ["0"])[0])
            with JOB_LOCK:
                self._json({"running": JOB["running"], "lines": JOB["lines"][after:],
                            "total": len(JOB["lines"]), "exit": JOB["exit"],
                            "result": JOB["result"], "started": JOB["started"]})
        else:
            self.send_error(404)

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            data = {}
        if u.path == "/api/config":
            main = pipeline.norm_path(data.get("source_root", ""))
            inbox = pipeline.norm_path(data.get("inbox_root", ""))
            if not os.path.isdir(main):
                self._json({"ok": False, "error": "主目录不存在：%s" % main})
                return
            if pipeline.root_too_broad(main):
                self._json({"ok": False, "error": "主目录太宽泛（不能选盘符、根目录或盘符第一层，如 / 或 /mnt/c）：%s" % main})
                return
            roots = [main]
            if inbox and inbox != main:
                if pipeline.root_too_broad(inbox):
                    self._json({"ok": False, "error": "收件箱太宽泛（不能选盘符、根目录或盘符第一层，如 / 或 /mnt/c）：%s" % inbox})
                    return
                try:
                    os.makedirs(inbox, exist_ok=True)
                except Exception as e:
                    self._json({"ok": False, "error": "无法创建收件箱：%s" % e})
                    return
                roots.append(inbox)
            cfg = pipeline.load_config()
            cfg["source_roots"] = roots
            pipeline.save_json(pipeline.CONFIG_PATH, cfg)
            SCAN_CACHE["payload"] = None
            self._json({"ok": True, "source_roots": roots})
        elif u.path == "/api/publish":
            ok, msg = start_job(data.get("mode", "select"), data.get("select") or [], bool(data.get("force")))
            self._json({"ok": ok, "message": msg}, 200 if ok else 409)
        else:
            self.send_error(404)


PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>博客发布器</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root { --bg:#0f1419; --panel:#181f27; --panel2:#1f2933; --line:#2a3542; --text:#e6edf3; --dim:#8b98a5; --accent:#3b82f6; --green:#22c55e; --orange:#f59e0b; --red:#ef4444; --purple:#a78bfa; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:14px/1.6 "Segoe UI","Microsoft YaHei",sans-serif; }
header { display:flex; align-items:center; gap:12px; padding:14px 20px; background:var(--panel); border-bottom:1px solid var(--line); position:sticky; top:0; z-index:5; }
header h1 { font-size:17px; margin:0; white-space:nowrap; }
header .root { color:var(--dim); font-size:12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; }
button { background:var(--panel2); color:var(--text); border:1px solid var(--line); border-radius:6px; padding:6px 14px; cursor:pointer; font-size:13px; }
button:hover { border-color:var(--accent); }
button.primary { background:var(--accent); border-color:var(--accent); color:#fff; }
button.primary:hover { filter:brightness(1.15); }
button:disabled { opacity:.45; cursor:not-allowed; }
.toolbar { display:flex; align-items:center; gap:10px; padding:15px 20px 5px; flex-wrap:wrap; }
.toolbar label { color:var(--dim); font-size:13px; display:flex; align-items:center; gap:6px; }
.spacer { flex:1; }
main { padding:10px 20px 24px; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:10px; margin-top:14px; overflow:hidden; }
.panel h2 { font-size:14px; margin:0; padding:11px 16px; border-bottom:1px solid var(--line); color:var(--dim); font-weight:600; display:flex; align-items:center; gap:8px; }
table { width:100%; border-collapse:collapse; }
th, td { text-align:left; padding:9px 14px; border-bottom:1px solid var(--line); font-size:13px; }
th { color:var(--dim); font-weight:500; font-size:12px; }
tr:last-child td { border-bottom:none; }
tr:hover td { background:#ffffff06; }
.badge { display:inline-block; padding:1px 9px; border-radius:20px; font-size:12px; border:1px solid; white-space:nowrap; }
.b-unpublished { color:var(--dim); border-color:var(--line); }
.b-published { color:var(--green); border-color:#1d4d33; background:#12291d; }
.b-updated { color:var(--orange); border-color:#5c4318; background:#2a2110; }
.b-error { color:var(--red); border-color:#5b2a2a; background:#2a1313; }
.b-blocked { color:var(--purple); border-color:#453664; background:#221a33; }
.tag { display:inline-block; padding:0 7px; border-radius:4px; font-size:11px; color:var(--accent); border:1px solid #274060; background:#122036; margin-right:4px; }
.tag.warn { color:var(--orange); border-color:#5c4318; background:#2a2110; }
.indent { display:inline-block; }
.dim { color:var(--dim); font-size:12px; }
.errline { color:#f0a0a0; font-size:12px; padding:4px 14px; }
#log { font:12px/1.55 Consolas,Menlo,monospace; white-space:pre-wrap; word-break:break-all; max-height:340px; min-height:120px; overflow-y:auto; padding:12px 16px; background:#0b0f14; color:#c9d4e0; }
#log .ok { color:var(--green); } #log .bad { color:var(--red); }
.modal { position:fixed; inset:0; background:#000a; display:none; align-items:center; justify-content:center; z-index:20; }
.modal.open { display:flex; }
.modal .box { background:var(--panel); border:1px solid var(--line); border-radius:12px; width:620px; max-width:94vw; padding:18px; }
.modal h2 { margin:0 0 6px; color:var(--text); font-size:15px; }
.frow { display:flex; gap:8px; margin-top:10px; align-items:center; }
.frow input { flex:1; background:#0b0f14; border:1px solid var(--line); color:var(--text); border-radius:6px; padding:8px 10px; font-size:13px; }
.frow label { color:var(--dim); font-size:12px; width:150px; flex:none; }
.frow.active input { border-color:var(--accent); }
.frow.active label { color:var(--accent); }
.dirbar { display:flex; gap:8px; align-items:center; margin-top:10px; }
.dirbar #curPath { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; background:#0b0f14; border:1px solid var(--line); border-radius:6px; padding:7px 10px; color:var(--dim); font-size:12px; }
.dirlist { max-height:240px; overflow-y:auto; border:1px solid var(--line); border-radius:8px; margin-top:10px; }
.dirlist div { padding:7px 12px; cursor:pointer; border-bottom:1px solid #ffffff08; display:flex; justify-content:space-between; }
.dirlist div:hover { background:#ffffff0a; }
.empty { color:var(--dim); padding:18px; text-align:center; font-size:13px; }
.hint { color:var(--dim); font-size:12px; margin-top:8px; }
.modal .row { display:flex; gap:8px; margin-top:12px; justify-content:flex-end; }
</style>
</head>
<body>
<header>
  <h1>博客发布器</h1>
  <span class="root" id="rootLabel"></span>
  <a href="http://localhost:__PREVIEW_PORT__" target="_blank"><button>打开预览</button></a>
  <button onclick="openSettings()">目录设置</button>
</header>

<div class="toolbar">
  <label><input type="checkbox" id="watch" checked> 自动监听</label>
  <label><input type="checkbox" id="forceChk"> 强制覆盖被占目录</label>
  <span class="spacer"></span>
  <button onclick="refresh(true)">刷新状态</button>
  <button onclick="doPublish('dry')">干跑预览</button>
  <button onclick="doPublish('select')">发布选中</button>
  <button class="primary" onclick="doPublish('all')">全部发布</button>
</div>

<main>
  <div class="panel">
    <h2>文章列表 <span class="dim" id="counts"></span></h2>
    <table>
      <thead><tr><th style="width:36px"><input type="checkbox" onchange="toggleAll(this)"></th><th>文章</th><th>源文件</th><th>标题</th><th>状态</th><th>图片</th><th>最近发布</th></tr></thead>
      <tbody id="arts"></tbody>
    </table>
    <div id="treeErrors"></div>
  </div>

  <div class="panel">
    <h2>未引用的图片 <span class="dim" id="orphanCount"></span></h2>
    <div id="orphans" class="dim" style="padding:10px 16px; font-size:12px;"></div>
  </div>

  <div class="panel">
    <h2>发布日志 <span class="dim" id="jobState"></span></h2>
    <div id="log" class="empty">等待任务…</div>
  </div>
</main>

<div class="modal" id="settings">
  <div class="box">
    <h2>目录设置</h2>
    <div class="frow" id="rowMain"><label>主目录（分类/章节）</label><input id="mainInput" placeholder="如 C:\Users\Eoooo\Desktop\Sephoration"><button onclick="pickField('main')">浏览</button></div>
    <div class="frow" id="rowInbox"><label>收件箱（可留空）</label><input id="inboxInput" placeholder="随手放的单篇笔记目录，如 桌面\博客收件箱"><button onclick="pickField('inbox')">浏览</button></div>
    <div class="dirbar"><span id="curPath"></span><button onclick="useCur()">选用此目录</button><button onclick="goUp()">上一层</button></div>
    <div class="dirlist" id="dirList"></div>
    <div class="hint" id="browseHint">先点「浏览」决定要改哪一行（高亮那行），再点文件夹进入；确认后点「选用此目录」填入。</div>
    <div class="row">
      <button onclick="closeSettings()">取消</button>
      <button class="primary" onclick="saveRoot()">保存</button>
    </div>
  </div>
</div>

<script>
let state = { data:null, busy:false, logCursor:0, curDir:"", pickField:null };
const WATCH_MS = __WATCH_MS__;
const fmt = s => s ? s : '—';

async function api(path, opt) {
  const r = await fetch(path, opt);
  return await r.json();
}

async function refresh(force) {
  const d = await api('/api/scan');
  if (d.scanning) { document.getElementById('counts').textContent = '正在扫描…'; return; }
  if (!d.ok) { document.getElementById('arts').innerHTML = '<tr><td colspan="7" class="empty">扫描失败：' + (d.error||'未知错误') + '</td></tr>'; return; }
  state.data = d;
  let label = '主目录: ' + d.main_root;
  if (d.inbox_roots.length) label += '　收件箱: ' + d.inbox_roots.join('、');
  document.getElementById('rootLabel').textContent = label;
  const c = d.counts;
  let cnt = '共 ' + c.total + ' 篇：未发布 ' + c.unpublished + '，有更新 ' + c.updated + '，已发布 ' + c.published + '，异常 ' + ((c.error||0)+(c.blocked||0));
  const inboxN = d.articles.filter(a => a.inbox).length;
  if (inboxN) cnt += '；其中收件箱 ' + inboxN + ' 篇';
  document.getElementById('counts').textContent = cnt;
  const tb = document.getElementById('arts');
  if (!d.articles.length) { tb.innerHTML = '<tr><td colspan="7" class="empty">源目录里还没找到文章（支持一章一个 md 直接放分类文件夹，或一章一个文件夹）</td></tr>'; }
  else {
    tb.innerHTML = d.articles.map(a => {
      const depth = a.rel_dir.split('/').length - 1;
      const name = a.rel_dir.split('/').pop();
      const errs = (a.errors||[]).map(e => '<div class="errline">↳ ' + e + '</div>').join('');
      const disabled = a.status==='error' ? 'disabled' : '';
      const tags = (a.inbox ? '<span class="tag">收件箱</span>' : '') + (a.ambiguous ? '<span class="tag warn">重名</span>' : '');
      const meta = ['路径: ' + a.rel_dir, '来源: ' + a.root_name, '源文件: ' + a.md_name,
        '修改: ' + fmt(a.md_mtime), '创建: ' + fmt(a.md_created),
        '首发: ' + fmt(a.first_published), '最近: ' + fmt(a.last_published),
        a.commit ? 'commit: #' + a.commit : ''].filter(Boolean).join(' ｜ ');
      return '<tr><td><input type="checkbox" class="pick" value="' + a.key + '" ' + disabled + '></td>'
        + '<td title="' + meta + '"><span class="indent" style="width:' + (depth*18) + 'px"></span>' + tags + name + errs + '</td>'
        + '<td class="dim" title="' + a.md_name + '">' + a.md_name + '</td>'
        + '<td>' + (a.title||'') + '</td>'
        + '<td><span class="badge b-' + a.status + '">' + a.status_text + '</span></td>'
        + '<td class="dim">' + a.images + '</td>'
        + '<td class="dim">' + fmt(a.last_published) + (a.commit ? ' <span title="commit">#' + a.commit + '</span>' : '') + '</td></tr>';
    }).join('');
  }
  document.getElementById('treeErrors').innerHTML = (d.errors||[]).map(e =>
    '<div class="errline">⚠ ' + (e.root_name ? e.root_name + '/ ' : '') + e.rel_dir + '：' + e.message + '（' + (e.md_names||[]).join('、') + '）</div>').join('');
  document.getElementById('orphanCount').textContent = d.orphans.length ? '(' + d.orphans.length + ')' : '(无)';
  document.getElementById('orphans').innerHTML = d.orphans.length ? d.orphans.join('<br>') : '没有未引用的图片';
}

function toggleAll(cb) { document.querySelectorAll('.pick').forEach(x => { if (!x.disabled) x.checked = cb.checked; }); }
function picked() { return [...document.querySelectorAll('.pick:checked')].map(x => x.value); }

async function doPublish(mode) {
  if (state.busy) return;
  const sel = picked();
  if (mode === 'select' && !sel.length) { alert('先勾选要发布的文章'); return; }
  if (mode === 'all' && !confirm('发布所有 未发布/有更新 的文章？')) return;
  const res = await api('/api/publish', { method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ mode: mode, select: sel, force: document.getElementById('forceChk').checked }) });
  if (!res.ok) { alert(res.message); return; }
  state.busy = true; state.logCursor = 0;
  document.getElementById('log').textContent = '';
  document.getElementById('log').className = '';
  document.getElementById('jobState').textContent = '进行中…';
  poll();
}

function logLine(t) {
  const el = document.getElementById('log');
  const div = document.createElement('div');
  div.textContent = t;
  if (/\[错误\]|\[拒绝\]|失败|错误/.test(t)) div.className = 'bad';
  else if (/已提交|已推送|通过|完成/.test(t)) div.className = 'ok';
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

async function poll() {
  const d = await api('/api/log?after=' + state.logCursor);
  state.logCursor = d.total;
  d.lines.forEach(logLine);
  if (d.running) { setTimeout(poll, 700); return; }
  state.busy = false;
  document.getElementById('jobState').textContent = d.exit === 0 ? '完成 ✓' : ('结束（退出码 ' + d.exit + '）');
  if (d.result && d.result.published && d.result.published.length)
    logLine('>> 成功 ' + d.result.published.length + ' 篇' + (d.result.published[0].url ? '（' + d.result.published.map(p=>p.url).join('、') + '）' : ''));
  refresh(true);
}

async function openSettings() {
  const cfg = await api('/api/config');
  const roots = cfg.source_roots || [];
  document.getElementById('mainInput').value = roots[0] || '';
  document.getElementById('inboxInput').value = roots[1] || '';
  setActive('main');
  await browse(roots[0] || '');
  document.getElementById('settings').classList.add('open');
}
function closeSettings() { document.getElementById('settings').classList.remove('open'); }

function setActive(f) {
  state.pickField = f;
  document.getElementById('rowMain').classList.toggle('active', f === 'main');
  document.getElementById('rowInbox').classList.toggle('active', f === 'inbox');
  document.getElementById('browseHint').textContent = (f === 'main' ? '正在选择：主目录' : '正在选择：收件箱') + '（高亮那行）。点文件夹进入，确认后点「选用此目录」填入。';
}

function pickField(f) {
  setActive(f);
  browse(document.getElementById(f + 'Input').value);
}

async function browse(p) {
  const d = await api('/api/dirs?path=' + encodeURIComponent(p||''));
  if (!d.ok) { if (p) alert(d.error); return; }
  state.curDir = d.path;
  document.getElementById('curPath').textContent = d.path;
  document.getElementById('dirList').innerHTML = d.dirs.map(x =>
    '<div onclick="browse(\'' + x.path.replace(/'/g, "\\'") + '\')"><span>' + x.name + (x.md_count ? ' <span class="dim">(' + x.md_count + ' md)</span>' : '') + '</span><span class="dim">›</span></div>'
  ).join('') || '<div class="empty">没有子文件夹</div>';
}

function useCur() {
  if (!state.curDir) return;
  document.getElementById(state.pickField + 'Input').value = state.curDir;
  document.getElementById('browseHint').textContent = '已填入：' + state.curDir + '（确认后点「保存」）';
}

function goUp() { const d = state.curDir.replace(/\/[^/]*$/, '') || '/'; browse(d); }
async function saveRoot() {
  const r = await api('/api/config', { method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ source_root: document.getElementById('mainInput').value, inbox_root: document.getElementById('inboxInput').value }) });
  if (!r.ok) { alert(r.error); return; }
  closeSettings();
  refresh(true);
}

document.getElementById('mainInput').addEventListener('keydown', e => { if (e.key === 'Enter') browse(e.target.value); });
document.getElementById('mainInput').addEventListener('focus', () => setActive('main'));
document.getElementById('inboxInput').addEventListener('focus', () => setActive('inbox'));
setInterval(() => { if (document.getElementById('watch').checked && !state.busy && !document.getElementById('settings').classList.contains('open')) refresh(true); }, WATCH_MS);
refresh(true);
</script>
</body>
</html>
"""


def main():
    cfg = pipeline.load_config()
    port = int(cfg.get("port", 8765))
    try:
        server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    except OSError:
        print("发布器已经在运行了，直接打开：http://localhost:%d" % port)
        time.sleep(3)
        return
    print("博客发布器已启动：http://localhost:%d" % port)
    print("（关闭本窗口或 Ctrl+C 退出）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

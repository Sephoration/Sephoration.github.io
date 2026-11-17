#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from urllib.parse import unquote

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.expanduser("~/.config/blog-publisher")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
MANIFEST_PATH = os.path.join(CONFIG_DIR, "manifest.json")
CONTENT_ROOT = os.path.join(REPO_ROOT, "content", "posts")
DEFAULT_SOURCE = "/mnt/c/Users/Eoooo/Desktop/博客大文件夹"
DEFAULT_INBOX = "/mnt/c/Users/Eoooo/Desktop/博客收件箱"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".bmp", ".avif", ".tif", ".tiff"}
MD_EXTS = (".md", ".markdown")
REF_RE = re.compile(r"!\[([^\]]*)\]\(\s*<?([^)\s<>]+?)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")
TS_RE = re.compile(r"-\d{8}-\d{6}(?:-\d+)?$")
FRONT_YAML_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
FRONT_TOML_RE = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.S)
DATE_YAML_RE = re.compile(r"^date\s*:", re.M)
DATE_TOML_RE = re.compile(r"^date\s*=", re.M)
TITLE_YAML_RE = re.compile(r"^title\s*:", re.M)
TITLE_TOML_RE = re.compile(r"^title\s*=", re.M)
TITLE_VAL_RE = re.compile(r"^title\s*[:=]\s*[\"']?(.+?)[\"']?\s*$", re.M)


def norm_path(p):
    p = (p or "").strip().strip('"').strip("'")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if m:
        p = "/mnt/" + m.group(1).lower() + "/" + m.group(2)
    return p.replace("\\", "/").rstrip("/") or "/"


def find_hugo(cfg=None):
    if cfg and cfg.get("hugo_bin"):
        return cfg["hugo_bin"]
    p = shutil.which("hugo")
    if p:
        return p
    cand = os.path.expanduser("~/.local/bin/hugo")
    if os.path.exists(cand):
        return cand
    return "hugo"


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load_config():
    cfg = load_json(CONFIG_PATH, {})
    fresh = not cfg
    legacy = cfg.pop("source_root", None)
    if "source_roots" not in cfg:
        cfg["source_roots"] = [legacy] if legacy else [DEFAULT_SOURCE, DEFAULT_INBOX]
    cfg["source_roots"] = [norm_path(r) for r in cfg["source_roots"] if r]
    cfg.setdefault("port", 8765)
    cfg.setdefault("preview_port", 1313)
    cfg.setdefault("watch_interval_sec", 15)
    cfg.setdefault("branch", "main")
    cfg.setdefault("hugo_bin", "")
    cfg.setdefault("hugo_args", [])
    cfg.setdefault("commit_message_template", "post: {verb}{title}")
    if fresh or legacy is not None:
        save_json(CONFIG_PATH, cfg)
    return cfg


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def img_sig(path):
    st = os.stat(path)
    return "%d:%d" % (st.st_size, st.st_mtime_ns)


def caption_for(name):
    stem = os.path.splitext(name)[0]
    m = TS_RE.search(stem)
    if m:
        stem = stem[: m.start()]
    return stem or os.path.splitext(name)[0]


def is_md(f):
    return f.lower().endswith(MD_EXTS) and not f.startswith(".") and not f.startswith("~")


def root_too_broad(p):
    parts = [x for x in norm_path(p).split("/") if x]
    return len(parts) < 3


def iter_tree(root):
    skip_dirs = {".git", "node_modules", ".obsidian", ".trash"}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not d.startswith(".") and d not in skip_dirs and not d.startswith("~")]
        yield dp, dns, fns


def find_articles(root):
    articles = []
    if not os.path.isdir(root):
        return articles, [{"rel_dir": ".", "md_names": [], "message": "源根目录不存在: %s" % root}]
    for dp, dns, fns in iter_tree(root):
        mds = sorted(f for f in fns if is_md(f))
        if not mds:
            continue
        rel = os.path.relpath(dp, root)
        folder = os.path.basename(dp)
        stems = [os.path.splitext(f)[0] for f in mds]
        if rel != "." and len(mds) == 1 and stems[0] == folder:
            articles.append({"rel_dir": rel, "md_name": mds[0],
                             "md_path": os.path.join(dp, mds[0]), "bare": False})
            continue
        for f, stem in zip(mds, stems):
            flat = stem if rel == "." else os.path.normpath(os.path.join(rel, stem))
            articles.append({"rel_dir": flat, "md_name": f,
                             "md_path": os.path.join(dp, f), "bare": rel == "."})
    return articles, []


def build_image_index(root):
    idx, all_imgs = {}, []
    for dp, dns, fns in iter_tree(root):
        for f in fns:
            if os.path.splitext(f)[1].lower() in IMG_EXTS:
                p = os.path.join(dp, f)
                all_imgs.append(p)
                idx.setdefault(f.lower(), []).append(p)
    return idx, all_imgs


def resolve_ref(ref, md_dir, root, img_index):
    if re.match(r"^[a-z][a-z0-9+.-]*://", ref, re.I) or ref.startswith("data:"):
        return None, "remote"
    ref = unquote(ref)
    cand = os.path.normpath(os.path.join(md_dir, ref))
    if os.path.isfile(cand):
        return cand, None
    cand2 = os.path.normpath(os.path.join(root, ref))
    if os.path.isfile(cand2):
        return cand2, None
    hits = img_index.get(os.path.basename(ref).lower(), [])
    if len(hits) == 1:
        return hits[0], None
    if len(hits) > 1:
        return None, "同名图片有多处：%s" % "、".join(os.path.relpath(h, root) for h in hits[:5])
    return None, "找不到图片"


def apply_front_matter(text, folder_name, auto_date):
    added = []
    m = FRONT_YAML_RE.match(text)
    if m:
        block, rest = m.group(1), text[m.end():]
        if not DATE_YAML_RE.search(block):
            lines = block.split("\n")
            at = len(lines)
            for i, ln in enumerate(lines):
                if TITLE_YAML_RE.match(ln):
                    at = i + 1
                    break
            lines.insert(at, "date: %s" % auto_date)
            block = "\n".join(lines)
            added.append("date")
        return "---\n%s\n---\n%s" % (block, rest), added
    m = FRONT_TOML_RE.match(text)
    if m:
        block, rest = m.group(1), text[m.end():]
        if not DATE_TOML_RE.search(block):
            lines = block.split("\n")
            at = len(lines)
            for i, ln in enumerate(lines):
                if TITLE_TOML_RE.match(ln):
                    at = i + 1
                    break
            lines.insert(at, 'date = "%s"' % auto_date)
            block = "\n".join(lines)
            added.append("date")
        return "+++\n%s\n+++\n%s" % (block, rest), added
    head = '---\ntitle: "%s"\ndate: %s\n---\n\n' % (folder_name, auto_date)
    added.extend(["title", "date"])
    return head + text, added


def extract_title(text, fallback):
    m = FRONT_YAML_RE.match(text) or FRONT_TOML_RE.match(text)
    if m:
        t = TITLE_VAL_RE.search(m.group(1))
        if t:
            return t.group(1).strip()
    return fallback


def fmt_ts(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def collect(cfg):
    roots = []
    for r in cfg.get("source_roots") or []:
        r = norm_path(r)
        if r and r not in roots:
            roots.append(r)
    entries, errors, root_data = [], [], {}
    for ri, root in enumerate(roots):
        name = os.path.basename(root.rstrip("/")) or root
        if not os.path.isdir(root):
            errors.append({"root": root, "root_name": name, "rel_dir": ".",
                           "md_names": [], "message": "目录不存在，已跳过：%s" % root})
            continue
        if root_too_broad(root):
            errors.append({"root": root, "root_name": name, "rel_dir": ".",
                           "md_names": [], "message": "目录过于宽泛，已跳过（请在设置里选更深一层的文件夹）：%s" % root})
            continue
        arts, errs = find_articles(root)
        for e in errs:
            e["root"] = root
            e["root_name"] = name
            errors.append(e)
        idx, all_imgs = build_image_index(root)
        root_data[root] = {"img_index": idx, "all_imgs": all_imgs, "root_name": name, "root_index": ri}
        for a in arts:
            a.update({"root": root, "root_name": name, "root_index": ri})
            entries.append(a)
    seen = {}
    for a in entries:
        seen[a["rel_dir"]] = seen.get(a["rel_dir"], 0) + 1
    for a in entries:
        if seen[a["rel_dir"]] > 1:
            a["key"] = "%s|%s" % (a["root_name"], a["rel_dir"])
            a["ambiguous"] = True
        else:
            a["key"] = a["rel_dir"]
            a["ambiguous"] = False
    return roots, entries, errors, root_data


def build_plan(article, img_index, manifest):
    root = article["root"]
    rel_dir = article["rel_dir"]
    key = article["key"]
    md_path = article["md_path"]
    folder = os.path.basename(os.path.normpath(os.path.join(root, rel_dir))) if rel_dir != "." else ""
    text = open(md_path, encoding="utf-8").read()
    title = extract_title(text, folder or os.path.splitext(article["md_name"])[0])
    st = os.stat(md_path)
    created = getattr(st, "st_birthtime", 0) or st.st_ctime
    plan = {
        "key": key,
        "rel_dir": rel_dir,
        "root": root,
        "root_name": article["root_name"],
        "root_index": article["root_index"],
        "ambiguous": article.get("ambiguous", False),
        "bare": article.get("bare", False),
        "title": title,
        "md_name": article["md_name"],
        "md_path": md_path,
        "md_mtime": fmt_ts(st.st_mtime),
        "md_created": fmt_ts(created),
        "target_rel": rel_dir,
        "target_abs": os.path.join(CONTENT_ROOT, rel_dir),
        "refs": 0,
        "errors": [],
        "warnings": [],
        "images": {},
        "captions": [],
    }
    refs = list(REF_RE.finditer(text))
    plan["refs"] = len(refs)
    res = []
    used = {}
    for m in refs:
        alt, ref = m.group(1), m.group(2)
        path, err = resolve_ref(ref, os.path.dirname(md_path), root, img_index)
        if err == "remote":
            res.append({"skip": True})
            continue
        if err:
            plan["errors"].append("引用 %s：%s" % (ref, err))
            res.append({"skip": True})
            continue
        base = os.path.basename(path)
        dest = base
        if dest in used and used[dest] != path:
            stem, ext = os.path.splitext(base)
            n = 2
            while "%s-%d%s" % (stem, n, ext) in used:
                n += 1
            dest = "%s-%d%s" % (stem, n, ext)
        used[dest] = path
        cap = caption_for(base)
        if not alt.strip():
            plan["captions"].append(cap)
        res.append({"source": path, "dest": dest, "caption": cap, "orig_alt": alt})
        plan["images"][dest] = path
    idx = [0]

    def mk_dest(dest):
        return "<%s>" % dest if re.search(r"[ ()<>]", dest) else dest

    def repl(m):
        r = res[idx[0]]
        idx[0] += 1
        if r.get("skip"):
            return m.group(0)
        return "![%s](%s)" % (r["caption"] if not r["orig_alt"].strip() else r["orig_alt"], mk_dest(r["dest"]))

    new_text = REF_RE.sub(repl, text)
    rec = manifest.get(key, {})
    auto_date = rec.get("auto_date") or date.today().isoformat()
    new_text, fm_added = apply_front_matter(new_text, folder or title, auto_date)
    plan["fm_added"] = fm_added
    plan["auto_date_used"] = auto_date if "date" in fm_added else None
    plan["new_md"] = new_text
    plan["md_hash"] = sha_text(new_text)
    plan["assets_sig"] = sha_text(json.dumps(sorted((d, img_sig(p)) for d, p in plan["images"].items()), ensure_ascii=False))
    return plan


def status_of(plan, manifest):
    tgt = plan["target_abs"]
    rec = manifest.get(plan["key"])
    if plan["errors"]:
        return "error"
    if not os.path.isdir(tgt):
        return "unpublished"
    if not rec:
        return "blocked"
    if rec.get("md_hash") != plan["md_hash"] or rec.get("assets_sig") != plan["assets_sig"]:
        return "updated"
    return "published"


def do_scan(cfg):
    roots, entries, errors, root_data = collect(cfg)
    manifest = load_json(MANIFEST_PATH, {})
    referenced = {}
    out = []
    for a in entries:
        rd = root_data[a["root"]]
        plan = build_plan(a, rd["img_index"], manifest)
        st = status_of(plan, manifest)
        for p in plan["images"].values():
            referenced.setdefault(a["root"], set()).add(os.path.normpath(p))
        rec = manifest.get(plan["key"], {})
        out.append({
            "key": plan["key"],
            "rel_dir": plan["rel_dir"],
            "root": plan["root"],
            "root_name": plan["root_name"],
            "root_index": plan["root_index"],
            "ambiguous": plan["ambiguous"],
            "bare": plan["bare"],
            "md_name": plan["md_name"],
            "md_mtime": plan["md_mtime"],
            "md_created": plan["md_created"],
            "title": plan["title"],
            "status": st,
            "errors": plan["errors"],
            "warnings": plan["warnings"],
            "refs": plan["refs"],
            "images": len(plan["images"]),
            "target": os.path.relpath(plan["target_abs"], REPO_ROOT),
            "first_published": rec.get("first_published"),
            "last_published": rec.get("published_at"),
            "commit": rec.get("commit"),
        })
    orphans = []
    for root in roots:
        if root not in root_data:
            continue
        ref = referenced.get(root, set())
        for p in root_data[root]["all_imgs"]:
            if os.path.normpath(p) not in ref:
                rel = os.path.relpath(p, root)
                orphans.append(rel if len(roots) == 1 else "%s/%s" % (root_data[root]["root_name"], rel))
    counts = {"total": len(out), "unpublished": 0, "published": 0, "updated": 0, "error": 0, "blocked": 0}
    for o in out:
        counts[o["status"]] = counts.get(o["status"], 0) + 1
    return {
        "ok": True,
        "source_roots": roots,
        "source_root": roots[0] if roots else "",
        "articles": sorted(out, key=lambda x: (x["root_index"], x["rel_dir"])),
        "errors": errors,
        "orphans": sorted(orphans),
        "counts": counts,
    }


def run_build(cfg):
    cmd = [find_hugo(cfg), *cfg.get("hugo_args", []), "--renderToMemory", "--quiet"]
    p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=900)
    if p.returncode != 0:
        tail = "\n".join((p.stderr or p.stdout or "").strip().splitlines()[-15:])
        return False, tail
    return True, ""


def git(*argv):
    return subprocess.run(["git", *argv], cwd=REPO_ROOT, capture_output=True, text=True)


def do_publish(cfg, args):
    roots, entries, tree_errors, root_data = collect(cfg)
    manifest = load_json(MANIFEST_PATH, {})
    by_key = {a["key"]: a for a in entries}

    if args.select:
        chosen = [by_key[k] for k in args.select if k in by_key]
        for k in args.select:
            if k not in by_key:
                print("跳过（源里找不到）：%s" % k)
    else:
        chosen = []
        for a in entries:
            plan = build_plan(a, root_data[a["root"]]["img_index"], manifest)
            if status_of(plan, manifest) in ("unpublished", "updated"):
                chosen.append(a)

    if not chosen:
        print("没有需要发布的文章")
        print("##RESULT## " + json.dumps({"ok": True, "published": [], "skipped": 0}, ensure_ascii=False))
        return 0

    plans = []
    failed = []
    for a in chosen:
        plan = build_plan(a, root_data[a["root"]]["img_index"], manifest)
        if plan["errors"]:
            failed.append({"key": plan["key"], "rel_dir": plan["rel_dir"], "errors": plan["errors"]})
            print("[错误] %s 不发布：" % plan["key"])
            for e in plan["errors"]:
                print("   - %s" % e)
            continue
        if status_of(plan, manifest) == "blocked" and not args.force:
            msg = "目标目录已存在但不在发布记录里（可能是你手动创建的内容），为避免覆盖已拒绝，确认替换请加 --force"
            failed.append({"key": plan["key"], "rel_dir": plan["rel_dir"], "errors": [msg]})
            print("[拒绝] %s：%s" % (plan["key"], msg))
            continue
        plans.append(plan)

    if not plans:
        print("选中的文章都有错误，未发布任何内容")
        print("##RESULT## " + json.dumps({"ok": False, "published": [], "failed": failed}, ensure_ascii=False))
        return 2

    for plan in plans:
        st = status_of(plan, manifest)
        print("[计划] %s" % plan["key"])
        print("   标题: %s | 状态: %s | 引用 %d 张 | 目标: %s" % (plan["title"], st, plan["refs"], os.path.relpath(plan["target_abs"], REPO_ROOT)))
        print("   图注: %s" % (("、".join(plan["captions"][:3]) + ("…" if len(plan["captions"]) > 3 else "")) if plan["captions"] else "(无空图注)"))
        if plan["fm_added"]:
            print("   自动补充 front matter: %s" % "、".join(plan["fm_added"]))

    if args.dry_run:
        print("干跑结束：以上 %d 篇将会被搬运（未改动任何文件）" % len(plans))
        print("##RESULT## " + json.dumps({"ok": True, "dry_run": True, "would_publish": [p["key"] for p in plans], "failed": failed}, ensure_ascii=False))
        return 0

    backups = []
    written = []
    ok = True
    for plan in plans:
        tgt = plan["target_abs"]
        if os.path.isdir(tgt):
            bak = tgt + ".bak-%d" % int(time.time())
            shutil.move(tgt, bak)
            backups.append((bak, tgt))
        os.makedirs(tgt, exist_ok=True)
        for dest, src in plan["images"].items():
            shutil.copy2(src, os.path.join(tgt, dest))
        with open(os.path.join(tgt, "index.md"), "w", encoding="utf-8") as f:
            f.write(plan["new_md"])
        written.append(plan)
        print("[写入] %s（%d 张图 + index.md）" % (plan["key"], len(plan["images"])))

    print("[构建] hugo 全量验证中…")
    ok, err_tail = run_build(cfg)
    if not ok:
        print("[构建失败] 回滚本次改动")
        for plan in written:
            if os.path.isdir(plan["target_abs"]):
                shutil.rmtree(plan["target_abs"])
        for bak, tgt in backups:
            shutil.move(bak, tgt)
        print(err_tail)
        print("##RESULT## " + json.dumps({"ok": False, "published": [], "build_error": err_tail, "failed": failed}, ensure_ascii=False))
        return 3

    print("[构建] 通过")

    def rec_of(plan, commit):
        old = manifest.get(plan["key"], {})
        return {
            "md_hash": plan["md_hash"],
            "assets_sig": plan["assets_sig"],
            "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "first_published": old.get("first_published") or time.strftime("%Y-%m-%d %H:%M:%S"),
            "commit": commit,
            "title": plan["title"],
            "target": os.path.relpath(plan["target_abs"], REPO_ROOT),
            "auto_date": plan["auto_date_used"] or old.get("auto_date"),
            "root": plan["root"],
            "root_name": plan["root_name"],
            "md_file": plan["md_name"],
            "md_mtime": plan["md_mtime"],
            "md_created": plan["md_created"],
        }

    results = []
    if args.no_git:
        print("[跳过] 按要求不提交 git（内容已写入，仅本地预览用）")
        for plan in written:
            url = "/posts/" + plan["target_rel"].replace(os.sep, "/") + "/"
            results.append({"key": plan["key"], "rel_dir": plan["rel_dir"], "title": plan["title"], "url": url, "commit": None})
    else:
        for plan in written:
            tgt = plan["target_abs"]
            git("add", "--", tgt)
            url = "/posts/" + plan["target_rel"].replace(os.sep, "/") + "/"
            if git("diff", "--cached", "--quiet", "--", tgt).returncode == 0:
                if plan["key"] not in manifest:
                    manifest[plan["key"]] = rec_of(plan, git("rev-parse", "--short", "HEAD").stdout.strip())
                results.append({"key": plan["key"], "rel_dir": plan["rel_dir"], "title": plan["title"], "url": url, "commit": manifest[plan["key"]].get("commit")})
                print("[git] %s 内容与已提交版本一致，跳过提交" % plan["key"])
                continue
            verb = "更新" if manifest.get(plan["key"]) else "新增"
            try:
                msg = cfg.get("commit_message_template", "post: {verb}{title}").format(verb=verb, title=plan["title"])
            except Exception:
                msg = "post: %s%s" % (verb, plan["title"])
            c = git("commit", "-m", msg, "--", tgt)
            if c.returncode != 0:
                print("[git] 提交失败：%s" % (c.stderr or c.stdout).strip()[-300:])
                ok = False
                continue
            h = git("rev-parse", "--short", "HEAD").stdout.strip()
            manifest[plan["key"]] = rec_of(plan, h)
            results.append({"key": plan["key"], "rel_dir": plan["rel_dir"], "title": plan["title"], "url": url, "commit": h})
            print("[git] 已提交 %s (%s)" % (msg, h))

        if not args.no_push:
            print("[git] 推送中…")
            p = git("push", "origin", cfg.get("branch", "main"))
            if p.returncode != 0:
                print("[git] 推送失败：%s" % (p.stderr or p.stdout).strip()[-300:])
                print("      （提交已在本地，可稍后手动 git push）")
            else:
                print("[git] 已推送，GitHub Actions 将自动部署")
        else:
            print("[git] 按要求不推送（提交已在本地）")
        save_json(MANIFEST_PATH, manifest)

    for bak, tgt in backups:
        shutil.rmtree(bak, ignore_errors=True)

    print("完成：成功 %d 篇，失败 %d 篇" % (len(results), len(failed)))
    print("##RESULT## " + json.dumps({"ok": ok and not failed, "published": results, "failed": failed}, ensure_ascii=False))
    return 0 if (ok and not failed) else 2


def main():
    ap = argparse.ArgumentParser(description="博客发布流水线：把源文件夹里的文章+图片搬运到 Hugo 并发布")
    ap.add_argument("--source", action="append", help="源根目录，可多次指定（默认读配置文件；首个为主目录，其余为收件箱）")
    ap.add_argument("--scan", action="store_true", help="只扫描并输出 JSON 状态")
    ap.add_argument("--dry-run", action="store_true", help="只报告不改动")
    ap.add_argument("--no-git", action="store_true", help="写入并构建验证，但不提交不推送")
    ap.add_argument("--no-push", action="store_true", help="提交但不推送")
    ap.add_argument("--select", nargs="*", help="指定要发布的文章（scan 输出的 key，可多个）")
    ap.add_argument("--force", action="store_true", help="允许覆盖非本工具发布的目标目录")
    args = ap.parse_args()

    cfg = load_config()
    if args.source:
        cfg["source_roots"] = [norm_path(s) for s in args.source if s.strip()]

    if args.scan:
        print(json.dumps(do_scan(cfg), ensure_ascii=False))
        return 0
    return do_publish(cfg, args)


if __name__ == "__main__":
    sys.exit(main())

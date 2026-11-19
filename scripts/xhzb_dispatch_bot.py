#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xhzb_dispatch_bot.py — GitHub Actions 触发机器人
作用: 每5小时调 GitHub API 的 workflow_dispatch 触发开源网刷新 workflow,
     绕开 GitHub 对 schedule 事件的降频限制(schedule 会被拉长到5~8小时+,
     dispatch 是即时响应的)。
用法: python3 xhzb_dispatch_bot.py [--force]
  --force  无视 last_dispatch.txt 时间戳, 强制触发一次(手动补跑用)
"""
import json, os, sys, time, urllib.request, datetime, argparse

TOKEN_FILE = os.path.expanduser("~/.config/gh_token")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_dispatch.txt")
REPO = "haohao7777235/backup-notes"
WORKFLOW = "refresh.yml"
INTERVAL = 30 * 60  # 30分钟

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(TOKEN_FILE):
        log(f"❌ 找不到 {TOKEN_FILE}")
        sys.exit(1)
    tok = open(TOKEN_FILE).read().strip()

    # 1) 距上次触发是否够 5 小时
    now = time.time()
    if not args.force and os.path.exists(STATE_FILE):
        try:
            last = float(open(STATE_FILE).read().strip())
            if now - last < INTERVAL:
                remain = (INTERVAL - (now - last)) / 60
                log(f"⏳ 距上次触发 {int((now-last)/60)} 分钟, 未到 5 小时, 跳过(还差 {remain:.0f} 分钟)")
                return
        except Exception:
            pass

    # 2) 触发 workflow_dispatch
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches"
    body = json.dumps({"ref": "main"}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "xhzb-dispatch-bot/1.0")
    req.add_header("Content-Type", "application/json")
    try:
        r = urllib.request.urlopen(req, timeout=20)
        if r.status == 204:
            open(STATE_FILE, "w").write(str(now))
            log(f"✅ 已触发 {REPO}/{WORKFLOW} (HTTP 204), 下次 {INTERVAL//60} 分钟后")
        else:
            log(f"⚠️ 触发返回 HTTP {r.status}")
    except urllib.error.HTTPError as e:
        # 429 = 限流; 403 可能 PAT 权限/2FA 等
        if e.code == 429:
            log("⚠️ GitHub API 限流(429), 下次再试")
        elif e.code == 403:
            log("❌ 403: 检查 PAT 权限(需 repo 写权限+actions 权限)")
        else:
            log(f"❌ HTTP {e.code}: {e.read().decode('utf-8','ignore')[:200]}")
        sys.exit(1)
    except Exception as e:
        log(f"❌ 网络错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

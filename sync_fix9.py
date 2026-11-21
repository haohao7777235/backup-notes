#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""one-shot: re-fetch missing 9 Live channels with HARD retry, then merge back"""
import json, time, sys, os, re, datetime, urllib.request

API_TOKEN = os.environ.get("API_TOKEN", "")
if not API_TOKEN:
    print("missing API_TOKEN", flush=True)
    sys.exit(1)

API = "https://www.xhzb.tw/index.php/api/tvbus_api/open"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# 缺的 9 台
MISSING = [
    {"cid": "31271", "title": "HBO_HD"},
    {"cid": "31272", "title": "HBOSignature"},
    {"cid": "31273", "title": "HBOHits"},
    {"cid": "31274", "title": "HBO family"},
    {"cid": "31284", "title": "好萊烏電影"},
    {"cid": "31287", "title": "龍祥電影"},
    {"cid": "30910", "title": "CINEMAX"},
    {"cid": "31525", "title": "star movies"},
    {"cid": "31527", "title": "法國時尚"},
]


def api_fetch(cid):
    try:
        req = urllib.request.Request(API, method="POST")
        req.add_header("Authorization", "Bearer " + API_TOKEN)
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", UA)
        req.add_header("Referer", "https://www.xhzb.tw/")
        req.add_header("Origin", "https://www.xhzb.tw")
        body = json.dumps({"channel_id": int(cid)}).encode()
        with urllib.request.urlopen(req, body, timeout=12) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        if d.get("code") == 1 and d.get("data") and "route" in d["data"]:
            u = d["data"]["route"].get("play_url")
            if u:
                return u
        return None
    except Exception:
        return None


def verify_url(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.xhzb.tw/"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(256)
            return r.status == 200, r.status
    except Exception:
        return False, 0


def hard_fetch(cid, title):
    """8 轮重试, 每轮 API 重新拿 token + 验证; 返回 (url or None, note)"""
    delays = [2, 3, 5, 8, 12, 18, 25, 30]
    for attempt in range(8):
        u = api_fetch(cid)
        if u:
            ok, code = verify_url(u)
            if ok:
                return u, "verified#%d" % (attempt + 1)
        time.sleep(delays[attempt])
    return None, "all-8-failed"


def main():
    results = {}
    for e in MISSING:
        u, note = hard_fetch(e["cid"], e["title"])
        results[e["title"]] = {"cid": e["cid"], "url": u, "note": note}
        print("%s: %s" % (e["title"], note), flush=True)
        time.sleep(1.0)

    # 合并进 xhzb_intl.m3u: 把 Live 组里这 9 台替换/补齐
    if os.path.exists("xhzb_intl.m3u"):
        lines = open("xhzb_intl.m3u", encoding="utf-8").read().splitlines()
        # 先删掉 Live 组里这 9 台的旧条目
        drop = {e["title"] for e in MISSING}
        out = ["#EXTM3U"]
        i = 0
        while i < len(lines):
            if lines[i].startswith("#EXTINF"):
                m = re.search(r'group-title="([^"]*)"', lines[i])
                g = m.group(1) if m else ""
                t = lines[i].split(",")[-1]
                if g == "Live" and t in drop:
                    i += 2
                    continue
                out.append(lines[i])
                if i + 1 < len(lines):
                    out.append(lines[i + 1])
                i += 2
            else:
                out.append(lines[i])
                i += 1
        # 在 Live 组末尾插入新拿到的
        live_insert = []
        for e in MISSING:
            r = results[e["title"]]
            if r["url"]:
                live_insert.append('#EXTINF:-1 group-title="Live",' + e["title"])
                live_insert.append(r["url"])
        if live_insert:
            # 插到第一个非 Live 条目之前
            pos = 0
            for idx, ln in enumerate(out):
                if ln.startswith("#EXTINF") and 'group-title="Live"' not in ln:
                    pos = idx
                    break
            else:
                pos = len(out)
            out[pos:pos] = live_insert
        open("xhzb_intl.m3u", "w", encoding="utf-8").write("\n".join(out) + "\n")
        live_count = sum(1 for ln in out if 'group-title="Live"' in ln)
        print("merged. Live count now:", live_count, flush=True)
    else:
        print("no m3u found", flush=True)


if __name__ == "__main__":
    main()

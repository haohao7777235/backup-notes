#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync: refresh Live group tokens ONLY, verify EVERY token, retry hard until live"""
import json, time, sys, os, re, subprocess, datetime, urllib.request

API_TOKEN = os.environ.get("API_TOKEN", "")
if not API_TOKEN:
    print("missing API_TOKEN", flush=True)
    sys.exit(1)

API = "https://www.xhzb.tw/index.php/api/tvbus_api/open"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# ---------------- 频道表: 同原版 ----------------
CHANNELS = [
    {"cid": "30898", "title": "LoveNature"},
    {"cid": "30909", "title": "amc电影"},
    {"cid": "30910", "title": "CINEMAX"},
    {"cid": "30911", "title": "ROCK Entertainment"},
    {"cid": "30928", "title": "ROCK_Action"},
    {"cid": "31264", "title": "Animaxa動漫"},
    {"cid": "31271", "title": "HBO_HD"},
    {"cid": "31272", "title": "HBOSignature"},
    {"cid": "31273", "title": "HBOHits"},
    {"cid": "31274", "title": "HBO family"},
    {"cid": "31284", "title": "好萊烏電影"},
    {"cid": "31287", "title": "龍祥電影"},
    {"cid": "31290", "title": "國家地理野生"},
    {"cid": "31295", "title": "采昌影劇"},
    {"cid": "31296", "title": "tvN"},
    {"cid": "31299", "title": "Discovery科學 SCI"},
    {"cid": "31300", "title": "Discovery DMAX"},
    {"cid": "31302", "title": "Discovery Asia"},
    {"cid": "31304", "title": "Discovery EVE"},
    {"cid": "31310", "title": "CinemaWorld頻道"},
    {"cid": "31311", "title": "Warner TV"},
    {"cid": "31013", "title": "FGM_gold電影"},
    {"cid": "31397", "title": "CATCHPLAY電影"},
    {"cid": "31406", "title": "History"},
    {"cid": "31453", "title": "动物星球"},
    {"cid": "31521", "title": "KIX電影"},
    {"cid": "31522", "title": "ROCK X EXTREME"},
    {"cid": "31524", "title": "MCE電影"},
    {"cid": "31525", "title": "star movies"},
    {"cid": "31527", "title": "法國時尚"},
]

# ---------------- 核心: 带验证的重试 ----------------

def api_fetch(cid):
    """调 API 拿 token, 返回 play_url 或 None"""
    try:
        req = urllib.request.Request(API, method="POST")
        req.add_header("Authorization", "Bearer " + API_TOKEN)
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", UA)
        req.add_header("Referer", "https://www.xhzb.tw/")
        req.add_header("Origin", "https://www.xhzb.tw")
        req.add_header("Accept", "application/json, text/plain, */*")
        req.add_header("Accept-Language", "zh-CN,zh;q=0.9")
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
    """拉 FLV 头验证: 200 且非空即活。返回 (ok, http_code)"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        req.add_header("Referer", "https://www.xhzb.tw/")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(256)
            return r.status == 200, r.status
    except Exception:
        return False, 0


def get_live_url(cid, title, old_url=None):
    """反复重试直到拿到验证通过的活 token。返回 (url, status)"""
    delays = [2, 4, 8, 16, 30]  # 指数退避
    for attempt in range(5):
        u = api_fetch(cid)
        if u:
            ok, code = verify_url(u)
            if ok:
                return u, "api+verified#%d" % (attempt + 1)
            time.sleep(delays[attempt])
        else:
            time.sleep(delays[attempt])
    # 5 轮 API 全部失败/无效 → 保底: 旧 URL 还活就用旧的
    if old_url:
        ok, code = verify_url(old_url)
        if ok:
            return old_url, "old-still-alive"
    return None, "all-failed"


def main():
    # 1. 读当前文件, 保留非 Live 组 + 记录 Live 旧 URL
    keep = []
    old_live = {}  # title -> url
    if os.path.exists("xhzb_intl.m3u"):
        lines = open("xhzb_intl.m3u", encoding="utf-8").read().splitlines()
        i = 0
        while i < len(lines):
            if lines[i].startswith("#EXTINF"):
                g = re.search(r'group-title="([^"]*)"', lines[i])
                group = g.group(1) if g else ""
                if group == "Live":
                    title = lines[i].split(",")[-1]
                    if i + 1 < len(lines):
                        old_live[title] = lines[i + 1].rstrip("/")
                    i += 2
                    continue
                keep.append(lines[i])
                if i + 1 < len(lines):
                    keep.append(lines[i + 1])
                i += 2
            else:
                keep.append(lines[i])
                i += 1

    # 2. 刷新 Live 组 (带验证 + 硬重试)
    ok = []
    fail = []
    for i, e in enumerate(CHANNELS):
        u, status = get_live_url(e["cid"], e["title"], old_live.get(e["title"]))
        if u:
            ok.append((e["cid"], e["title"], u))
        else:
            fail.append(e["title"])
        if (i + 1) % 30 == 0 or status == "all-failed":
            print("...%d/%d ok=%d fail=%d" % (i + 1, len(CHANNELS), len(ok), len(fail)), flush=True)
        time.sleep(0.3)  # 低频, 防风控

    # 3. 重组输出
    out = ["#EXTM3U"]
    for cid, title, u in ok:
        out.append('#EXTINF:-1 group-title="Live",' + title)
        out.append(u)
    out.extend(keep)
    content = "\n".join(out) + "\n"
    open("xhzb_intl.m3u", "w", encoding="utf-8").write(content)
    total = content.count("#EXTINF")
    print("done: Live=%d keep=%d total=%d" % (len(ok), len(keep) // 2, total), flush=True)
    if fail:
        print("FAILED: " + repr(fail), flush=True)

    # 4. 时间戳
    with open("last_sync.txt", "w", encoding="utf-8") as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat() + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync: refresh Live group tokens only, KEEP other groups intact"""
import json, subprocess, time, sys, os, urllib.request, re

API_TOKEN = os.environ.get("API_TOKEN", "")
if not API_TOKEN:
    print("missing API_TOKEN", flush=True)
    sys.exit(1)
API = "https://www.xhzb.tw/index.php/api/tvbus_api/open"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

CHANNELS = [
    {"cid": "30892", "title": "CNN"},
    {"cid": "30898", "title": "LoveNature"},
    {"cid": "30904", "title": "FRANCE24"},
    {"cid": "30907", "title": "半島國際新聞"},
    {"cid": "30909", "title": "amc电影"},
    {"cid": "30910", "title": "CINEMAX"},
    {"cid": "30911", "title": "ROCK Entertainment"},
    {"cid": "30912", "title": "NickJr"},
    {"cid": "30916", "title": "Global Trekker"},
    {"cid": "30919", "title": "TRACE Sport Stars"},
    {"cid": "30921", "title": "Pet Club TV"},
    {"cid": "30922", "title": "FightSports"},
    {"cid": "30923", "title": "Love Nature 4K"},
    {"cid": "30924", "title": "BBC World News"},
    {"cid": "30925", "title": "DW"},
    {"cid": "30926", "title": "NHK World"},
    {"cid": "30928", "title": "Arirang TV"},
    {"cid": "30930", "title": "Bloomberg"},
    {"cid": "30932", "title": "CNBC"},
    {"cid": "30935", "title": "Sky News"},
    {"cid": "30937", "title": "France 24 English"},
    {"cid": "30940", "title": "Al Jazeera"},
    {"cid": "30943", "title": "RT News"},
    {"cid": "30946", "title": "TRT World"},
    {"cid": "30949", "title": "CGTN"},
    {"cid": "30952", "title": "CNA"},
    {"cid": "30955", "title": "Channel NewsAsia"},
    {"cid": "30958", "title": "ABC Australia"},
    {"cid": "30961", "title": "TV5Monde"},
    {"cid": "30964", "title": "Deutsche Welle"},
    {"cid": "30967", "title": "Euronews"},
    {"cid": "30970", "title": "i24NEWS"},
    {"cid": "30973", "title": "News18"},
    {"cid": "30976", "title": "WION"},
    {"cid": "30979", "title": "KBS World"},
    {"cid": "30982", "title": "MBC"},
    {"cid": "30985", "title": "SBS"},
    {"cid": "30988", "title": "Arirang"},
    {"cid": "30991", "title": "TVBS"},
    {"cid": "30994", "title": "台視"},
    {"cid": "30997", "title": "民視"},
    {"cid": "31000", "title": "東森新聞"},
    {"cid": "31003", "title": "中天新聞"},
    {"cid": "31006", "title": "三立新聞"},
    {"cid": "31009", "title": "TVBS-N"},
    {"cid": "31012", "title": "非凡新聞"},
    {"cid": "31015", "title": "年代新聞"},
    {"cid": "31018", "title": "寰宇新聞"},
    {"cid": "31021", "title": "壹電視"},
    {"cid": "31024", "title": "udn新聞"},
    {"cid": "31027", "title": "大愛"},
    {"cid": "31030", "title": "人間衛視"},
    {"cid": "31033", "title": "客家電視"},
    {"cid": "31036", "title": "原住民族電視"},
    {"cid": "31039", "title": "國會頻道1"},
    {"cid": "31042", "title": "國會頻道2"},
    {"cid": "31045", "title": "新聞頻道"},
    {"cid": "31048", "title": "公視"},
    {"cid": "31051", "title": "華視"},
    {"cid": "31054", "title": "中視"},
    {"cid": "31057", "title": "台視綜合"},
    {"cid": "31060", "title": "中視新聞"},
    {"cid": "31063", "title": "民視新聞"},
    {"cid": "31066", "title": "華視新聞"},
    {"cid": "31069", "title": "公視台語台"},
    {"cid": "31072", "title": "TaiwanPlus"},
    {"cid": "31075", "title": "Discovery"},
    {"cid": "31078", "title": "Animal Planet"},
    {"cid": "31081", "title": "Nat Geo"},
    {"cid": "31084", "title": "History"},
    {"cid": "31087", "title": "TLC"},
    {"cid": "31090", "title": "Food Network"},
    {"cid": "31093", "title": "HGTV"},
    {"cid": "31096", "title": "Travel Channel"},
    {"cid": "31099", "title": "Crime + Investigation"},
    {"cid": "31102", "title": "Investigation Discovery"},
    {"cid": "31105", "title": "Smithsonian"},
    {"cid": "31108", "title": "Science"},
    {"cid": "31111", "title": "CuriosityStream"},
    {"cid": "31114", "title": "Motor Trend"},
    {"cid": "31117", "title": "Outdoor Channel"},
    {"cid": "31120", "title": "Fishing TV"},
    {"cid": "31123", "title": "Golf Channel"},
    {"cid": "31126", "title": "NBA TV"},
    {"cid": "31129", "title": "NFL Network"},
    {"cid": "31132", "title": "MLB Network"},
    {"cid": "31135", "title": "NHL Network"},
    {"cid": "31138", "title": "ESPN"},
    {"cid": "31141", "title": "ESPN2"},
    {"cid": "31144", "title": "ESPN News"},
    {"cid": "31147", "title": "FOX Sports"},
    {"cid": "31150", "title": "FS2"},
    {"cid": "31153", "title": "beIN Sports"},
    {"cid": "31156", "title": "beIN Sports 2"},
    {"cid": "31159", "title": "beIN Sports 3"},
    {"cid": "31162", "title": "Sky Sports"},
    {"cid": "31165", "title": "Sky Sports 2"},
    {"cid": "31168", "title": "Sky Sports 3"},
    {"cid": "31171", "title": "Sky Sports News"},
    {"cid": "31174", "title": "BT Sport"},
    {"cid": "31177", "title": "BT Sport 2"},
    {"cid": "31180", "title": "BT Sport 3"},
    {"cid": "31183", "title": "Eurosport"},
    {"cid": "31186", "title": "Eurosport 2"},
    {"cid": "31189", "title": "DAZN"},
    {"cid": "31192", "title": "DAZN 2"},
    {"cid": "31195", "title": "Sport TV"},
    {"cid": "31198", "title": "Eleven Sports"},
    {"cid": "31201", "title": "Eleven Sports 2"},
    {"cid": "31204", "title": "Premier Sports"},
    {"cid": "31207", "title": "Motorvision"},
    {"cid": "31210", "title": "Racing"},
    {"cid": "31213", "title": "At The Races"},
    {"cid": "31216", "title": "Racing UK"},
    {"cid": "31219", "title": "CCTV"},
    {"cid": "31222", "title": "CCTV2"},
    {"cid": "31225", "title": "CCTV4"},
    {"cid": "31228", "title": "CCTV9"},
    {"cid": "31231", "title": "CCTV13"},
    {"cid": "31234", "title": "CGTN"},
    {"cid": "31237", "title": "CGTN Documentary"},
    {"cid": "31240", "title": "CGTN Arabic"},
    {"cid": "31243", "title": "CGTN Spanish"},
    {"cid": "31246", "title": "CGTN Français"},
    {"cid": "31249", "title": "China Global TV"},
    {"cid": "31252", "title": "鳳凰衛視"},
    {"cid": "31255", "title": "鳳凰資訊"},
    {"cid": "31258", "title": "鳳凰香港"},
    {"cid": "31261", "title": "星空衛視"},
    {"cid": "31264", "title": "Astro"},
    {"cid": "31267", "title": "Astro AOD"},
    {"cid": "31270", "title": "Astro Ria"},
    {"cid": "31273", "title": "TVB"},
    {"cid": "31276", "title": "TVB Jade"},
    {"cid": "31279", "title": "TVB Pearl"},
    {"cid": "31282", "title": "ViuTV"},
    {"cid": "31285", "title": "Now TV"},
    {"cid": "31288", "title": "HBO"},
    {"cid": "31291", "title": "HBO Family"},
    {"cid": "31294", "title": "HBO Hits"},
    {"cid": "31297", "title": "HBO Signature"},
    {"cid": "31300", "title": "Cinemax"},
    {"cid": "31303", "title": "TCM"},
    {"cid": "31306", "title": "AXN"},
    {"cid": "31309", "title": "FOX"},
    {"cid": "31312", "title": "FOX Movies"},
    {"cid": "31315", "title": "FOX Family"},
    {"cid": "31318", "title": "FOX Crime"},
    {"cid": "31321", "title": "Star Movies"},
    {"cid": "31324", "title": "Star World"},
    {"cid": "31327", "title": "Star Chinese"},
    {"cid": "31330", "title": "Lifetime"},
    {"cid": "31333", "title": "AMC"},
    {"cid": "31336", "title": "Crime"},
    {"cid": "31339", "title": "Syfy"},
    {"cid": "31342", "title": "FX"},
    {"cid": "31345", "title": "Comedy Central"},
    {"cid": "31348", "title": "MTV"},
    {"cid": "31351", "title": "VH1"},
    {"cid": "31354", "title": "Cartoon Network"},
    {"cid": "31357", "title": "Disney Channel"},
    {"cid": "31360", "title": "Disney Jr"},
    {"cid": "31363", "title": "Nickelodeon"},
    {"cid": "31366", "title": "DreamWorks"},
    {"cid": "31369", "title": "Boomerang"},
    {"cid": "31372", "title": "CBeebies"},
    {"cid": "31375", "title": "BabyTV"},
    {"cid": "31378", "title": "Tiny Pop"},
    {"cid": "31381", "title": "Kix"},
    {"cid": "31384", "title": "Pop Max"},
    {"cid": "31387", "title": "Pop"},
    {"cid": "31390", "title": "CBBC"},
    {"cid": "31393", "title": "CITV"},
    {"cid": "31396", "title": "Milkshake"},
    {"cid": "31399", "title": "Nick Jr"},
    {"cid": "31401", "title": "CARTOONITO"},
    {"cid": "31395", "title": "FGM_gold電影"},
    {"cid": "31488", "title": "經典卡通"},
    {"cid": "31489", "title": "精選動漫"},
    {"cid": "31490", "title": "幸福空間居家"},
    {"cid": "31497", "title": "生命電視"},
    {"cid": "31504", "title": "哆啦A夢"},
    {"cid": "31526", "title": "經典迪士尼"},
]


def fetch(cid):
    for attempt in range(3):
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
            with urllib.request.urlopen(req, body, timeout=10) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
            if d.get("code") == 1 and d.get("data") and "route" in d["data"]:
                u = d["data"]["route"].get("play_url")
                if u:
                    return u
            return None
        except Exception:
            pass
        time.sleep(1.0)
    return None


def main():
    # 1. 读当前文件, 保留非 Live 组
    keep = []
    if os.path.exists("xhzb_intl.m3u"):
        lines = open("xhzb_intl.m3u", encoding="utf-8").read().splitlines()
        i = 0
        while i < len(lines):
            if lines[i].startswith("#EXTINF"):
                g = re.search(r'group-title="([^"]*)"', lines[i])
                group = g.group(1) if g else ""
                if group == "Live":
                    i += 2  # skip Live EXTINF + URL
                    continue
                keep.append(lines[i])
                if i + 1 < len(lines):
                    keep.append(lines[i + 1])
                i += 2
            else:
                keep.append(lines[i])
                i += 1

    # 2. 刷新 Live 组
    ok = []
    fail = []
    for i, e in enumerate(CHANNELS):
        u = fetch(e["cid"])
        if u:
            ok.append((e["cid"], e["title"], u))
        else:
            fail.append(e["title"])
        if (i + 1) % 30 == 0:
            print(f"...{i+1}/{len(CHANNELS)} ok={len(ok)}", flush=True)
        time.sleep(0.4)

    # 3. 重组: Live + 保留组
    out = ["#EXTM3U"]
    for cid, title, u in ok:
        out.append(f'#EXTINF:-1 group-title="Live",{title}')
        out.append(u)
    out.extend(keep)
    content = "\n".join(out) + "\n"
    open("xhzb_intl.m3u", "w", encoding="utf-8").write(content)
    total = content.count("#EXTINF")
    print(f"done: Live={len(ok)} keep={len(keep)//2} total={total}", flush=True)
    if len(ok) < 60:
        print("too few, abort commit", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

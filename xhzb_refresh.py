#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""星火国际 145 台 token 每30分钟刷新 (GitHub Actions 版)
在 GitHub Actions 服务器上运行, 不依赖本地电脑:
- 调星火 tvbus_api/open 换新 token
- 生成 xhzb_intl.m3u
- commit 回 GitHub 仓库 (workflow 自动 commit)
"""
import json, subprocess, time, sys, os, urllib.request

# 星火 API token (来自 App 逆向, 长期有效, 每天拉取不限次)
XHZB_TOKEN = os.environ.get("XHZB_TOKEN", "88c1fdc1567923276e9b31998424babdd5ae0fdaa3b9b640aaf0b4bf18b8bbba")
API = "https://www.xhzb.tw/index.php/api/tvbus_api/open"

# map: 145 台 cid -> title (从 VM xhzb_intl_map.json 导出)
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
    {"cid": "30928", "title": "ROCK_Action"},
    {"cid": "31184", "title": "BBC Earth"},
    {"cid": "31185", "title": "BBC Lifestyle"},
    {"cid": "31261", "title": "台灣戲劇"},
    {"cid": "31263", "title": "JET綜合"},
    {"cid": "31264", "title": "Animaxa動漫"},
    {"cid": "31265", "title": "CBeebies"},
    {"cid": "31266", "title": "哈哈台"},
    {"cid": "31267", "title": "邵氏電影"},
    {"cid": "31268", "title": "邵氏武俠"},
    {"cid": "31271", "title": "HBO_HD"},
    {"cid": "31272", "title": "HBOSignature"},
    {"cid": "31273", "title": "HBOHits"},
    {"cid": "31274", "title": "HBO family"},
    {"cid": "31277", "title": "中旺電視"},
    {"cid": "31278", "title": "美食星球"},
    {"cid": "31279", "title": "壹電影"},
    {"cid": "31280", "title": "壹綜合"},
    {"cid": "31282", "title": "EVE戲劇"},
    {"cid": "31283", "title": "EVE旅遊"},
    {"cid": "31284", "title": "好萊烏電影"},
    {"cid": "31286", "title": "霹靂台灣"},
    {"cid": "31287", "title": "龍祥電影"},
    {"cid": "31288", "title": "中華特產"},
    {"cid": "31289", "title": "環球旅遊"},
    {"cid": "31290", "title": "國家地理野生"},
    {"cid": "31291", "title": "鏡電視新聞"},
    {"cid": "31294", "title": "華藝中文"},
    {"cid": "31295", "title": "采昌影劇"},
    {"cid": "31296", "title": "tvN"},
    {"cid": "31297", "title": "HGTV居家樂活頻道"},
    {"cid": "31298", "title": "CNEX紀實頻道"},
    {"cid": "31299", "title": "Discovery科學 SCI"},
    {"cid": "31300", "title": "Discovery DMAX"},
    {"cid": "31301", "title": "Lifetime"},
    {"cid": "31302", "title": "Discovery Asia"},
    {"cid": "31303", "title": "INULTRA"},
    {"cid": "31304", "title": "Discovery EVE"},
    {"cid": "31306", "title": "LiveABC互動英語頻道"},
    {"cid": "31307", "title": "空中英語教室"},
    {"cid": "31308", "title": "豬哥亮歌廳秀"},
    {"cid": "31309", "title": "達文西頻道"},
    {"cid": "31310", "title": "CinemaWorld頻道"},
    {"cid": "31311", "title": "Warner TV"},
    {"cid": "31345", "title": "TNTSports2"},
    {"cid": "31346", "title": "TNTSports3"},
    {"cid": "31347", "title": "TNTSports4"},
    {"cid": "31351", "title": "beINSports XTRA"},
    {"cid": "31352", "title": "TSN1"},
    {"cid": "31353", "title": "TSN2"},
    {"cid": "31354", "title": "TSN3"},
    {"cid": "31355", "title": "TSN4"},
    {"cid": "31356", "title": "TSN5"},
    {"cid": "31357", "title": "歐洲體育1"},
    {"cid": "31358", "title": "歐洲體育2"},
    {"cid": "31359", "title": "ESPNU"},
    {"cid": "31360", "title": "ESPN"},
    {"cid": "31361", "title": "ESPN 2"},
    {"cid": "31362", "title": "NBA TV Philippines"},
    {"cid": "31363", "title": "Sky_Mix"},
    {"cid": "31364", "title": "Sky_Cricket"},
    {"cid": "31365", "title": "Sky_MainEvent"},
    {"cid": "31366", "title": "SKY_PREMIER_LEAGUE"},
    {"cid": "31367", "title": "Sky_Racing"},
    {"cid": "31368", "title": "ESPN 4"},
    {"cid": "31369", "title": "Sky_sports+"},
    {"cid": "31370", "title": "Sky_Tennis"},
    {"cid": "31372", "title": "UFC"},
    {"cid": "31373", "title": "NBATV"},
    {"cid": "31374", "title": "RED BULL TV 紅牛極限運動"},
    {"cid": "31375", "title": "WWE"},
    {"cid": "31376", "title": "五星體育"},
    {"cid": "31377", "title": "智林體育"},
    {"cid": "31378", "title": "甘霖體育"},
    {"cid": "31379", "title": "MyVideo體育"},
    {"cid": "31380", "title": "DAZN體育"},
    {"cid": "31381", "title": "勁爆體育"},
    {"cid": "31382", "title": "Hami大聯盟1"},
    {"cid": "31383", "title": "Hami大聯盟2"},
    {"cid": "31384", "title": "Hami足球1"},
    {"cid": "31385", "title": "Hami WBC1"},
    {"cid": "31386", "title": "Hami體育1"},
    {"cid": "31394", "title": "影迷數位紀實"},
    {"cid": "31397", "title": "CATCHPLAY電影"},
    {"cid": "31398", "title": "momo綜合"},
    {"cid": "31399", "title": "尼克兒童頻道"},
    {"cid": "31400", "title": "CN卡通頻道"},
    {"cid": "31401", "title": "CARTOONITO"},
    {"cid": "31402", "title": "DreamWorks 夢工廠動畫"},
    {"cid": "31403", "title": "麥卡貝綜藝"},
    {"cid": "31405", "title": "亞洲旅遊"},
    {"cid": "31406", "title": "History"},
    {"cid": "31407", "title": "SPOTV1"},
    {"cid": "31408", "title": "SPOTV2"},
    {"cid": "31442", "title": "CRIM+罪案偵緝頻道"},
    {"cid": "31453", "title": "动物星球"},
    {"cid": "31454", "title": "高點綜合"},
    {"cid": "31485", "title": "新加坡MU"},
    {"cid": "31487", "title": "客家電視"},
    {"cid": "31491", "title": "原住民電視"},
    {"cid": "31492", "title": "車迷TV"},
    {"cid": "31493", "title": "滾動力rollor"},
    {"cid": "31495", "title": "fun探索娛樂"},
    {"cid": "31496", "title": "灣聲線上音樂廳"},
    {"cid": "31499", "title": "大愛電視"},
    {"cid": "31500", "title": "大愛二台"},
    {"cid": "31501", "title": "好消息"},
    {"cid": "31502", "title": "好消息2"},
    {"cid": "31503", "title": "經典電影"},
    {"cid": "31505", "title": "SMART知識"},
    {"cid": "31506", "title": "第1商業"},
    {"cid": "31508", "title": "Hami體育2台"},
    {"cid": "31509", "title": "MOMO親子"},
    {"cid": "31512", "title": "beIN SPORTS NBA （MSG_NBA）"},
    {"cid": "31513", "title": "NBA SportsNet 360"},
    {"cid": "31514", "title": "ESPN3"},
    {"cid": "31515", "title": "時尚運動X"},
    {"cid": "31516", "title": "getwin sport運動台"},
    {"cid": "31517", "title": "BBC NEWS"},
    {"cid": "31518", "title": "CNA新聞"},
    {"cid": "31519", "title": "FOX NEWS"},
    {"cid": "31520", "title": "CI 罪案偵查頻道"},
    {"cid": "31521", "title": "KIX電影"},
    {"cid": "31522", "title": "ROCK X EXTREME"},
    {"cid": "31523", "title": "HITS電影"},
    {"cid": "31524", "title": "MCE電影"},
    {"cid": "31525", "title": "star movies"},
    {"cid": "31527", "title": "法國時尚"},
    {"cid": "31528", "title": "TV5MOND生活時尚"},
    {"cid": "31529", "title": "電影原聲CMusic"},
    {"cid": "31530", "title": "CLASSICA 古典樂"},
    {"cid": "31531", "title": "TRACE Urban"},
    {"cid": "31532", "title": "Mezzo Live"}
]

def main():
    ok = []
    fail = []
    for i, e in enumerate(CHANNELS):
        cid, title = e["cid"], e["title"]
        try:
            req = urllib.request.Request(API, method="POST")
            req.add_header("Authorization", "Bearer " + XHZB_TOKEN)
            req.add_header("Content-Type", "application/json")
            body = json.dumps({"channel_id": int(cid)}).encode()
            with urllib.request.urlopen(req, body, timeout=10) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
            if d.get("code") == 1 and d.get("data") and "route" in d["data"]:
                u = d["data"]["route"].get("play_url")
                if u:
                    ok.append((cid, title, u))
                    continue
            fail.append((cid, title))
        except Exception:
            fail.append((cid, title))
        if (i + 1) % 30 == 0:
            print(f"...{i+1}/{len(CHANNELS)} 成功{len(ok)}", flush=True)
        time.sleep(0.3)

    lines = ["#EXTM3U"]
    for cid, title, u in ok:
        lines.append(f'#EXTINF:-1 group-title="星火国际",{title}')
        lines.append(u)
    content = "\n".join(lines) + "\n"
    with open("xhzb_intl.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"完成: 成功 {len(ok)}/{len(CHANNELS)}, 失败 {len(fail)}: {[t for _,t in fail][:10]}", flush=True)
    if len(ok) < 60:
        print("⚠️ 成功率过低 (<60), workflow 将不 commit", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

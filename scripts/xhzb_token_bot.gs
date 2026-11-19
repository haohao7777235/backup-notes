/**
 * xhzb_token_bot.gs — 星火 token 自动续期(Google Apps Script 版)
 * 
 * 部署步骤:
 * 1. 打开 https://script.google.com 新建项目, 粘贴本文件
 * 2. 点左侧"触发器" → 添加触发器:
 *    - 函数: main
 *    - 时间来源: 时间驱动
 *    - 类型: 分钟定时器
 *    - 间隔: 每 30 分钟
 * 3. 在"项目设置"里添加脚本属性(不以明文出现在代码里):
 *    - XHZB_TOKEN = 星火会员 token
 *    - GH_PAT     = GitHub PAT(仓库 backup-notes 写权限)
 * 4. 手动运行一次 main() 授权(Google 会要求同意权限)
 * 
 * 功能: 拉 152 台 Live 新 token → 生成 m3u → PUT 回 GitHub backup-notes
 */

// ============ 配置 ============
var API = "https://www.xhzb.tw/index.php/api/tvbus_api/open";
var REPO = "haohao7777235/backup-notes";           // 开源网仓库
var M3U_PATH = "xhzb_intl.m3u";                     // 仓库内文件路径
var UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36";

// 152 台 Live 频道 (cid, title) — 从仓库 sync.py 的 CHANNELS 复制
var CHANNELS = [
  ["30892","CNN"],["30898","LoveNature"],["30904","FRANCE24"],["30907","半島國際新聞"],
  ["30909","amc电影"],["30910","CINEMAX"],["30911","ROCK Entertainment"],["30912","NickJr"],
  ["30916","Global Trekker"],["30919","TRACE Sport Stars"],["30921","Pet Club TV"],["30922","FightSports"],
  ["30928","ROCK_Action"],["31184","BBC Earth"],["31185","BBC Lifestyle"],["31261","台灣戲劇"],
  ["31263","JET綜合"],["31264","Animaxa動漫"],["31265","CBeebies"],["31266","哈哈台"],
  ["31267","邵氏電影"],["31268","邵氏武俠"],["31271","HBO_HD"],["31272","HBOSignature"],
  ["31273","HBOHits"],["31274","HBO family"],["31277","中旺電視"],["31278","美食星球"],
  ["31279","壹電影"],["31280","壹綜合"],["31282","EVE戲劇"],["31283","EVE旅遊"],
  ["31284","好萊烏電影"],["31286","霹靂台灣"],["31287","龍祥電影"],["31288","中華特產"],
  ["31289","環球旅遊"],["31290","國家地理野生"],["31291","鏡電視新聞"],["31294","華藝中文"],
  ["31295","采昌影劇"],["31296","tvN"],["31297","HGTV居家樂活頻道"],["31298","CNEX紀實頻道"],
  ["31299","Discovery科學 SCI"],["31300","Discovery DMAX"],["31301","Lifetime"],["31302","Discovery Asia"],
  ["31303","INULTRA"],["31304","Discovery EVE"],["31306","LiveABC互動英語頻道"],["31307","空中英語教室"],
  ["31308","豬哥亮歌廳秀"],["31309","達文西頻道"],["31310","CinemaWorld頻道"],["31311","Warner TV"],
  ["31345","TNTSports2"],["31346","TNTSports3"],["31347","TNTSports4"],["31351","beINSports XTRA"],
  ["31352","TSN1"],["31353","TSN2"],["31354","TSN3"],["31355","TSN4"],["31356","TSN5"],
  ["31357","歐洲體育1"],["31358","歐洲體育2"],["31359","ESPNU"],["31360","ESPN"],["31361","ESPN 2"],
  ["31362","NBA TV Philippines"],["31363","Sky_Mix"],["31364","Sky_Cricket"],["31365","Sky_MainEvent"],
  ["31366","SKY_PREMIER_LEAGUE"],["31367","Sky_Racing"],["31368","ESPN 4"],["31369","Sky_sports+"],
  ["31370","Sky_Tennis"],["31372","UFC"],["31373","NBATV"],["31374","RED BULL TV 紅牛極限運動"],
  ["31375","WWE"],["31376","五星體育"],["31377","智林體育"],["31378","甘霖體育"],["31379","MyVideo體育"],
  ["31380","DAZN體育"],["31381","勁爆體育"],["31382","Hami大聯盟1"],["31383","Hami大聯盟2"],
  ["31384","Hami足球1"],["31385","Hami WBC1"],["31386","Hami體育1"],["31394","影迷數位紀實"],
  ["31397","CATCHPLAY電影"],["31398","momo綜合"],["31399","尼克兒童頻道"],["31400","CN卡通頻道"],
  ["31401","CARTOONITO"],["31402","DreamWorks 夢工廠動畫"],["31403","麥卡貝綜藝"],["31405","亞洲旅遊"],
  ["31406","History"],["31407","SPOTV1"],["31408","SPOTV2"],["31442","CRIM+罪案偵緝頻道"],
  ["31453","动物星球"],["31454","高點綜合"],["31485","新加坡MU"],["31487","客家電視"],
  ["31491","原住民電視"],["31492","車迷TV"],["31493","滾動力rollor"],["31495","fun探索娛樂"],
  ["31496","灣聲線上音樂廳"],["31499","大愛電視"],["31500","大愛二台"],["31501","好消息"],
  ["31502","好消息2"],["31503","經典電影"],["31505","SMART知識"],["31506","第1商業"],
  ["31508","Hami體育2台"],["31509","MOMO親子"],["31512","beIN SPORTS NBA （MSG_NBA）"],
  ["31513","NBA SportsNet 360"],["31514","ESPN3"],["31515","時尚運動X"],["31516","getwin sport運動台"],
  ["31517","BBC NEWS"],["31518","CNA新聞"],["31519","FOX NEWS"],["31520","CI 罪案偵查頻道"],
  ["31521","KIX電影"],["31522","ROCK X EXTREME"],["31523","HITS電影"],["31524","MCE電影"],
  ["31525","star movies"],["31527","法國時尚"],["31528","TV5MOND生活時尚"],["31529","電影原聲CMusic"],
  ["31530","CLASSICA 古典樂"],["31531","TRACE Urban"],["31532","Mezzo Live"]
];

// ============ 主函数(定时器调用这个) ============
function main() {
  var xhzbToken = PropertiesService.getScriptProperties().getProperty("XHZB_TOKEN");
  var ghPat = PropertiesService.getScriptProperties().getProperty("GH_PAT");
  if (!xhzbToken || !ghPat) {
    Logger.log("❌ 缺少 XHZB_TOKEN 或 GH_PAT 属性, 请在项目设置添加");
    return;
  }

  var ok = [], fail = [];
  for (var i = 0; i < CHANNELS.length; i++) {
    var cid = CHANNELS[i][0], title = CHANNELS[i][1];
    try {
      var resp = UrlFetchApp.fetch(API, {
        method: "post",
        contentType: "application/json",
        headers: {
          "Authorization": "Bearer " + xhzbToken,
          "User-Agent": UA,
          "Referer": "https://www.xhzb.tw/",
          "Origin": "https://www.xhzb.tw"
        },
        payload: JSON.stringify({ channel_id: parseInt(cid) }),
        muteHttpExceptions: true,
        timeoutSeconds: 15
      });
      var d = JSON.parse(resp.getContentText());
      if (d.code == 1 && d.data && d.data.route && d.data.route.play_url) {
        ok.push([cid, title, d.data.route.play_url]);
      } else {
        fail.push(title);
      }
    } catch (e) {
      fail.push(title + "(" + e + ")");
    }
    if (i % 30 == 0) Utilities.sleep(300); // 每30台小歇, 避免触发风控
  }

  Logger.log("成功 " + ok.length + "/" + CHANNELS.length + ", 失败: " + fail.join(","));
  if (ok.length < 60) { Logger.log("⚠️ 成功率过低, 不推送"); return; }

  // 生成 m3u(保留台港直连 + TVATA活源两组不覆盖!)
  var lines = ["#EXTM3U"];
  // Live 组(新 token)
  for (var j = 0; j < ok.length; j++) {
    lines.push('#EXTINF:-1 group-title="Live",' + ok[j][1]);
    lines.push(ok[j][2]);
  }
  // 追加直连组(从当前仓库文件读, 原样保留)
  try {
    var existing = getRepoFile(M3U_PATH, ghPat);
    var keepGroups = ["台港直连", "TVATA活源"];
    var inKeep = false;
    var lines2 = existing.split("\n");
    for (var k = 0; k < lines2.length; k++) {
      var l = lines2[k];
      if (l.indexOf("#EXTINF") == 0) {
        var m = l.match(/group-title="([^"]+)"/);
        inKeep = m && keepGroups.indexOf(m[1]) >= 0;
      }
      if (inKeep) lines.push(l);
    }
  } catch (e) { Logger.log("读取直连组失败: " + e); }

  var content = lines.join("\n") + "\n";
  putRepoFile(M3U_PATH, content, ghPat);
  Logger.log("✅ 已推送 m3u(" + ok.length + " Live + 直连组保留)");
}

// ============ GitHub 文件读写 ============
function getRepoFile(path, pat) {
  var url = "https://api.github.com/repos/" + REPO + "/contents/" + path;
  var resp = UrlFetchApp.fetch(url, {
    headers: { "Authorization": "Bearer " + pat, "User-Agent": UA },
    muteHttpExceptions: true
  });
  if (resp.getResponseCode() != 200) throw new Error("GET " + resp.getResponseCode());
  var d = JSON.parse(resp.getContentText());
  return Utilities.newBlob(Utilities.base64Decode(d.content)).getDataAsString();
}

function putRepoFile(path, content, pat) {
  var url = "https://api.github.com/repos/" + REPO + "/contents/" + path;
  var existing = UrlFetchApp.fetch(url, {
    headers: { "Authorization": "Bearer " + pat, "User-Agent": UA },
    muteHttpExceptions: true
  });
  var sha = null;
  if (existing.getResponseCode() == 200) {
    sha = JSON.parse(existing.getContentText()).sha;
  }
  var body = {
    message: "token refresh " + new Date().toISOString(),
    content: Utilities.base64Encode(content),
    sha: sha
  };
  var resp = UrlFetchApp.fetch(url, {
    method: "put",
    contentType: "application/json",
    headers: { "Authorization": "Bearer " + pat, "User-Agent": UA },
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });
  if (resp.getResponseCode() != 200 && resp.getResponseCode() != 201) {
    throw new Error("PUT " + resp.getResponseCode() + " " + resp.getContentText().slice(0, 200));
  }
}

# 星火国际 145 台(自动刷新)

GitHub Actions 每 30 分钟自动调用星火 API 换取新 token,生成最新 `xhzb_intl.m3u` 并推送。

## 订阅地址(电视 FONGMI)

```
https://raw.githubusercontent.com/haohao7777235/private-iptv/main/xhzb_intl.m3u
```

## 说明

- 台数: 145 台(星火国际分类)
- token 有效期约 30 分钟, Actions 自动刷新, 无需手动
- 若某台拉取失败, 该台跳过(不写入 m3u), 其余台正常

## 状态

- 最近刷新: 见仓库 commit 记录

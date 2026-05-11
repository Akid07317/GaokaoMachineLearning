# 数据获取状态

## 已确认的官方入口

- `2024` 本科普通批院校专业组投档最低分数线（物理）：[广西招生考试院](https://www.gxeea.cn/view/content_624_30533.htm)
- `2025` 本科普通批院校专业组投档最低分数线（物理）：[广西招生考试院](https://www.gxeea.cn/view/content_1013_31850.htm)
- `2024` 普通类物理一分一档索引页：[阳光高考](https://gaokao.chsi.com.cn/gkxx/zc/ss/202406/20240625/2293300016.html)
- `2025` 普通类物理一分一档索引页：[阳光高考](https://gaokao.chsi.com.cn/gkxx/zc/ss/202506/20250626/2293390989.html)
- `2024` 历年一位一档查询入口：[广西阳光志愿信息服务系统](https://zyfz.gxeea.cn/Main/Chengji/CJ_Yiweiyidang_2024.aspx)
- `2025` 阳光志愿系统说明页：[广西招生考试院](https://www.gxeea.cn/view/content_722_31619.htm)
- 招生章程统一入口：[阳光高考](https://gaokao.chsi.com.cn/zsgs/zhangcheng/)

## 终端抓取结果

- `gaokao.chsi.com.cn` 可以从终端下载到页面，但当前拿到的是反爬壳页面，不含正文数据。
- `www.gxeea.cn` 直连时出现 `LibreSSL SSL_connect: SSL_ERROR_SYSCALL` 或 `Empty reply from server`。
- `zyfz.gxeea.cn` 直连时出现 `SSL connection timeout`。

## 当前结论

- 现在已经把“官方入口在哪里”这件事梳理清楚了，见 [source_list.csv](../source_list.csv)。
- 真实抓取尝试结果已经落到本地的 `reports/fetch_status.csv`，该文件作为生成状态表默认不提交。
- 终端自动抓取需要做多策略处理，不能只假设 `curl` 直接可用。
- 在官方站点未稳定直连前，最现实的策略是：
  1. 先用仓库里的来源清单和抓取脚本固化入口与状态。
  2. 优先抓取能通过的公开索引页。
  3. 对 `gxeea.cn`、`zyfz.gxeea.cn` 这类站点，保留浏览器人工导出或后续更稳的抓取通道。

## 下一步建议

- 先补 `scripts/fetch_public_sources.py` 的运行结果日志。
- 如果你愿意稍后配合一次浏览器侧操作，我们可以把 2024、2025 的真实表格页面手动导出到 `raw_data/`，然后我这边继续清洗。

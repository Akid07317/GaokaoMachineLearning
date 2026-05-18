# 数据获取状态

## 已确认的官方入口

- `2024` 本科普通批院校专业组投档最低分数线（物理）：[广西招生考试院](https://www.gxeea.cn/view/content_624_30533.htm)
- `2025` 本科普通批院校专业组投档最低分数线（物理）：[广西招生考试院](https://www.gxeea.cn/view/content_1013_31850.htm)
- `2024` 普通类物理一分一档索引页：[阳光高考](https://gaokao.chsi.com.cn/gkxx/zc/ss/202406/20240625/2293300016.html)
- `2025` 普通类物理一分一档索引页：[阳光高考](https://gaokao.chsi.com.cn/gkxx/zc/ss/202506/20250626/2293390989.html)
- `2024` 历年一位一档查询入口：[广西阳光志愿信息服务系统](https://zyfz.gxeea.cn/Main/Chengji/CJ_Yiweiyidang_2024.aspx)
- `2025` 阳光志愿系统说明页：[广西招生考试院](https://www.gxeea.cn/view/content_722_31619.htm)
- 招生章程统一入口：[阳光高考](https://gaokao.chsi.com.cn/zsgs/zhangcheng/)

## 当前抓取结果

- 本地终端直连 `gxeea.cn`、`zyfz.gxeea.cn` 时仍会遇到 SSL 兼容问题。
- 服务器端在关闭证书校验后，已经成功抓到 7 份公开页面。
- `gaokao.chsi.com.cn` 目前仍会返回 `412 Precondition Failed`。
- `jyt.gxzf.gov.cn` 当前返回 `403 Forbidden`。

## 当前结论

- 现在已经把“官方入口在哪里”这件事梳理清楚了，见 [source_list.csv](../source_list.csv)。
- 真实抓取尝试结果已经落到本地的 `reports/fetch_status.csv`，该文件作为生成状态表默认不提交。
- 服务器已经证明：`gxeea.cn` 和 `zyfz.gxeea.cn` 可以通过 `curl -k` 抓到真实页面内容。
- 现在手上已有可直接抽表的公开数据：
  1. `2024` 本科普通批物理类投档线
  2. `2025` 本科普通批物理类投档线
  3. `2024` 物理类一分一档两种口径
- 仍需重点补齐：
  1. `2025` 物理类一分一档
  2. `2026` 招生计划
  3. 登录后系统内的 `招生计划`、`选院校`、`投档分数明细`

## 下一步建议

- 继续在服务器上使用登录态抓系统内页。
- 对已抓到的公开 HTML 持续抽表并沉淀到 `clean_data/`。
- 把 `2025` 一分一档作为优先缺口继续广撒网查找。

## 2026-05-15 最新核对

- 当前时间核对为 `2026-05-15 00:49 CST`。
- 新增确认了一条 **2025 一分一档发布时间线索**：
  - 广西招生考试院《[广西2025年普通高校招生录取最低控制分数线公布](https://www.gxeea.cn/view/content_722_31610.htm)》明确写到，`2025-06-25 13:00` 会在“招考新闻”和“系统导航-成绩查询”等栏目公布 `2025` 普通高考一分一档表。
- 新增确认了一条 **2025 志愿系统开放线索**：
  - 广西招生考试院《[6月25日15:00起，高考志愿填报系统正式开放](https://www.gxeea.cn/view/content_722_31604.htm)》给出了电脑端和手机端入口说明，可作为后续登录态抓系统内 `招生计划`、`选院校`、`分数线` 的公开指引。
- 新增确认了一个 **阳光志愿系统公开能力说明**：
  - 广西高考志愿填报辅助系统注册页公开写明，系统可查看“历年录取数据”和“本年的全部批次招生计划”，说明 `2026` 招生计划更可能在系统内而不是公开静态页完整放出。
- 截至本次核对，**还没有确认到公开可直接抓取的 `2026` 本科普通批物理类招生计划页面**；目前更像是：
  1. 公开站先放政策、时间、入口说明；
  2. 具体计划仍需等待系统开放或登录态进入后获取。
- 新增确认一个 **2025 普通类一位一档官方直达入口**：
  - 官方页为 [2025年一位一档查询](https://www.gxeea.cn/2025gxywyd/index.html)。
  - 服务器侧已验证该入口可访问，且物理类细分页也可直达，例如：
    - `https://www.gxeea.cn/2025gxywyd/2025_yifenyidang_wuli_qg_339.html`
    - `https://www.gxeea.cn/2025gxywyd/2025_yifenyidang_wuli_qn_382.html`
  - 这意味着 `2025` 物理类一分一档缺口已经从“仅有公告/搜索线索”推进到“已确认官方查询入口与细分页可达”，后续可以优先走服务器侧批量抽取。

## 2026-05-16 最新推进

- 新增确认一个 **目标校隐藏 JSON 数据源突破口**：
  - 华北电力大学本科招生页并非纯静态页，`招生计划` 和 `往年分数` 页面内嵌了可直接抓取的 JSON 数据源：
    - `https://goto.ncepu.edu.cn/common/plan_json.json`
    - `https://goto.ncepu.edu.cn/common/aii_json.json`
    - `https://goto.ncepu.edu.cn/common/major_json.json`
  - 三个源已通过服务器抓取并同步回本地：
    - [raw_data/ncepu_json/plan_json.json](/Users/don/Documents/New%20project/raw_data/ncepu_json/plan_json.json:1)
    - [raw_data/ncepu_json/aii_json.json](/Users/don/Documents/New%20project/raw_data/ncepu_json/aii_json.json:1)
    - [raw_data/ncepu_json/major_json.json](/Users/don/Documents/New%20project/raw_data/ncepu_json/major_json.json:1)
  - 已进一步抽出广西子集：
    - [ncepu_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/ncepu_guangxi_plan_rows.csv:1) `77` 行
    - [ncepu_guangxi_summary_score_rows.csv](/Users/don/Documents/New%20project/reports/ncepu_guangxi_summary_score_rows.csv:1) `5` 行
    - [ncepu_guangxi_major_score_rows.csv](/Users/don/Documents/New%20project/reports/ncepu_guangxi_major_score_rows.csv:1) `43` 行
  - 这说明：即使部分学校官网不直接给出“广西”静态详情页，也可能在页面脚本层暴露出可直接抽取的结构化数据。

- 新增确认一组 **福州大学官方招生正文页**：
  - [福州大学2026年普通高考招生章程](https://zsb.fzu.edu.cn/info/1067/2632.htm) `2026-05-11`
  - [福州大学2025年普通高考招生章程](https://zsb.fzu.edu.cn/info/1067/2332.htm) `2025-05-12`
  - [福州大学2025年本科招生专业选考科目要求](https://zsb.fzu.edu.cn/info/1067/2334.htm) `2025-05-14`
  - [2025年福州大学高校专项分省分专业计划](https://zsb.fzu.edu.cn/info/1070/2345.htm) `2025-05-28`
  - 以上正文已通过服务器抓取并落地到：
    - [discovery_fzu_followup_fetch.csv](/Users/don/Documents/New%20project/reports/discovery_fzu_followup_fetch.csv:1)
    - [raw_data/fzu_followup](/Users/don/Documents/New%20project/raw_data/fzu_followup)

- 新增整理一组 **福州大学官方广西计划 / 历年录取页来源**：
  - 广西计划查询页：
    - 直达页：`https://zsks2.fzu.edu.cn/zhaosheng/?zsnf-1,syssmc-6,jhlbmc-1,klmc-1`
    - 入口页：`https://zsb.fzu.edu.cn/zscx/jhcx.htm`
    - 已整理：
      - [fzu_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/fzu_guangxi_plan_rows.csv:1) `34` 行 `2025` 广西物理类计划
  - 历年录取页：
    - 直达页：`https://zsks2.fzu.edu.cn/linianluqu/`
    - 入口页：`https://zsb.fzu.edu.cn/zscx/lnfs.htm`
    - 已整理：
      - [fzu_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/fzu_guangxi_score_rows.csv:1) `69` 行 `2024-2025` 广西物理类专业分
  - 价值：补出一条新的官方“计划查询页 + 历年录取页”组合源，覆盖广西 `2025` 物理类计划和 `2024-2025` 物理类专业分；结果里还保留了选科要求、备注和专业级最高/最低分字段。

- 当前判断更新：
  1. 广西官方 `2026` 本科普通批物理类公开静态计划页仍未确认。
  2. 但目标校官网侧已经证明：继续广撒网不仅能发现入口页，还能打到隐藏 JSON 和正式招生正文页。
  3. 后续优先值得复用的思路是：先抓入口 HTML，再专门查 `data-url` / `json_filter` / 列表页中的隐藏结构化源。

- 新增确认一组 **北京交通大学官方隐藏 JSON 数据源**：
  - 入口页：
    - [历年分数](http://zsw.bjtu.edu.cn/zsw/lnfs.html)
    - [招生计划](http://zsw.bjtu.edu.cn/zsw/zsjh.html)
  - 服务器侧已从页面脚本确认并抓到接口：
    - `http://zsw.bjtu.edu.cn/f/ajax_lnfs_param`
    - `http://zsw.bjtu.edu.cn/f/ajax_lnfs`
    - `http://zsw.bjtu.edu.cn/f/ajax_zsjh_param`
    - `http://zsw.bjtu.edu.cn/f/ajax_zsjh`
  - 已同步回本地缓存：
    - [raw_data/bjtu_followup/ajax_lnfs_param.json](/Users/don/Documents/New%20project/raw_data/bjtu_followup/ajax_lnfs_param.json:1)
    - [raw_data/bjtu_followup/ajax_lnfs_guangxi_2025_physics_ordinary_wuhua.json](/Users/don/Documents/New%20project/raw_data/bjtu_followup/ajax_lnfs_guangxi_2025_physics_ordinary_wuhua.json:1)
    - [raw_data/bjtu_followup/ajax_zsjh_param.json](/Users/don/Documents/New%20project/raw_data/bjtu_followup/ajax_zsjh_param.json:1)
    - [raw_data/bjtu_followup/ajax_zsjh_guangxi_2025_physics_ordinary_wuhua.json](/Users/don/Documents/New%20project/raw_data/bjtu_followup/ajax_zsjh_guangxi_2025_physics_ordinary_wuhua.json:1)
  - 已进一步抽出广西 `2025` 物理普通类子集：
    - [bjtu_guangxi_physics_ordinary_plan_rows.csv](/Users/don/Documents/New%20project/reports/bjtu_guangxi_physics_ordinary_plan_rows.csv:1) `7` 行
    - [bjtu_guangxi_physics_ordinary_score_group_rows.csv](/Users/don/Documents/New%20project/reports/bjtu_guangxi_physics_ordinary_score_group_rows.csv:1) `3` 行
    - [bjtu_guangxi_physics_ordinary_major_score_rows.csv](/Users/don/Documents/New%20project/reports/bjtu_guangxi_physics_ordinary_major_score_rows.csv:1) `7` 行
  - 这说明北京交通大学这条线已经从“入口页线索”推进到“可直接抽取广西物理普通类结构化计划和分数明细”。

- 新增整理三组 **项目缓存中已落地但此前未正式登记的官方 API 数据源**：
  - 西安电子科技大学官方 LQXX 接口：
    - 计划源：`https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList`
    - 页面入口：`https://zsxc.xidian.edu.cn/auth/zsdata/lqxx`
    - 已抽出：
      - [xidian_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/xidian_guangxi_plan_rows.csv:1) `11` 行
      - [xidian_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/xidian_guangxi_score_rows.csv:1) `17` 行
    - 价值：补出广西 `2025` 物理类计划与专业分明细。
  - 长安大学官方 LQXX 接口：
    - 计划/分数源：`https://zsdata.chd.edu.cn/lqxx/s/api/front/lqxx/getList`
    - 页面入口：`https://zsdata.chd.edu.cn/zsdata/lqxx/#/lnfs`
    - 已抽出：
      - [changan_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/changan_guangxi_plan_rows.csv:1) `37` 行
      - [changan_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/changan_guangxi_score_rows.csv:1) `32` 行
    - 价值：补出广西 `2025` 物理类计划与 `2024` 物理类专业分明细。
  - 华东理工大学官方 LQXX2 接口：
    - 计划源：`https://bkzsdata.ecust.edu.cn/lqxx/s/api/front/lqxx2/getList?type=zsjh`
    - 分数源：`https://bkzsdata.ecust.edu.cn/lqxx/s/api/front/lqxx2/getList?type=lnfs`
    - 页面入口：`https://bkzsdata.ecust.edu.cn/zsdata/lqxx/`
    - 已抽出：
      - [ecust_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/ecust_guangxi_plan_rows.csv:1) `25` 行
      - [ecust_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/ecust_guangxi_score_rows.csv:1) `25` 行
    - 价值：补出广西 `2024-2025` 物理类计划与专业分明细，并带校区、选科要求、备注信息。
  - 华东理工大学 `2022` 官方查询入口锚点：
    - [华东理工大学本科招生小程序开通](https://zsb.ecust.edu.cn/2022/0410/c2323a143238/page.htm) `2022-04-10`
    - 来源：华东理工大学本科招生网
    - 正文明确说明学校侧小程序可查询：
      - 学院专业介绍
      - 历年分数
      - 招生计划
    - 价值：把已登记的官方计划 / 分数 API 再向前补上一条带明确发布日期的学校侧入口锚点，方便后续比较查询入口与能力范围变化。

  - 本轮阻塞更新：
  - 上海大学 FineUI 查询页仍是公开页，但当前仓库里的表单回放变体未能把广西结果成功提交出来。
  - 北京科技大学、大连海事大学虽然暴露出与北京交通大学同族的 `ajax_lnfs_param` / `ajax_zsjh_param` 接口，但服务器侧返回的是显式 `{"state":0,"msg":"禁止访问"}`，不值得继续在同一角度上硬耗。

- 新增整理三组 **更多已缓存官方 API 数据源**：
  - 河海大学官方 API：
    - 计划源：`https://zsw.hhu.edu.cn/api/zsjh/jhList`
    - 分数源：`https://zsw.hhu.edu.cn/api/lsfs/fsList`
    - 页面入口：`https://zsw.hhu.edu.cn/zhaoshengjihua.html`
    - 已抽出：
      - [hehai_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/hehai_guangxi_plan_rows.csv:1) `44` 行
      - [hehai_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/hehai_guangxi_score_rows.csv:1) `94` 行
    - 价值：补出广西 `2025` 物理类计划以及 `2024-2025` 物理类专业分，且计划备注中带有培养校区轮转说明。
  - 武汉理工大学官方 API：
    - 计划源：`https://zs.whut.edu.cn/enroll-info/recruitScheme/selRecruitByProvinceAndYearAndSubjectType.do`
    - 分数源：`https://zs.whut.edu.cn/enroll-info/recruitByMajor/selRecruitByProvinceAndYearAndSubjectType.do`
    - 页面入口：`https://zs.whut.edu.cn/enroll-info/recruitScheme/list.do`
    - 已抽出：
      - [wuhan_ligong_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/wuhan_ligong_guangxi_plan_rows.csv:1) `29` 行
      - [wuhan_ligong_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/wuhan_ligong_guangxi_score_rows.csv:1) `53` 行
    - 价值：补出广西 `2025` 物理类计划以及 `2024-2025` 物理类专业分，含卓越实验班与选考要求。
  - 南京理工大学官方 API：
    - 计划源：`https://zsb.njust.edu.cn/lqPain/initDateCon`
    - 分数源：`https://zsb.njust.edu.cn/lqScore/initDateWebCon`
    - 页面入口：`https://zsb.njust.edu.cn/lqjh_fsx.html`
    - 已抽出：
      - [njust_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/njust_guangxi_plan_rows.csv:1) `13` 行
      - [njust_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/njust_guangxi_score_rows.csv:1) `29` 行
    - 价值：补出广西 `2025` 物理类计划以及 `2023-2025` 物理类专业分。

- 新增整理两组 **官方直达页 / 官方 PDF 来源**：
  - 合肥工业大学广西直达详情页：
    - 直达页：`http://bkzs.hfut.edu.cn/f/zsjhAndLqfs/广西`
    - 已抽出：
      - [hfut_guangxi_overview_rows.csv](/Users/don/Documents/New%20project/reports/hfut_guangxi_overview_rows.csv:1) `3` 行总览
      - [hfut_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/hfut_guangxi_plan_rows.csv:1) `51` 行 `2025` 物理类计划
      - [hfut_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/hfut_guangxi_score_rows.csv:1) `41` 行 `2022-2024` 物理类分数
    - 价值：这是少见的“同一官方详情页同时给计划和近三年分数”的广西直达页，覆盖密度很高。
  - 河北工业大学官方 PDF / 通知页：
    - 计划 PDF：`https://zs.hebut.edu.cn/Upload/file/20250630/1751266683401513.pdf`
    - 通知页：`https://zs.hebut.edu.cn/2025-07-12/216.html`
    - 已抽出：
      - [hebut_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/hebut_guangxi_plan_rows.csv:1) `10` 行 `2025` 广西计划
      - [hebut_guangxi_batch_notice_rows.csv](/Users/don/Documents/New%20project/reports/hebut_guangxi_batch_notice_rows.csv:1) `1` 行批次通知记录
    - 价值：补出广西本科普通批录取完成通知，并把计划 PDF 里的广西列切出来。
    - 风险：当前 PDF 解析里存在个别长专业名粘连，说明这条可用但仍需人工复核后再进入更高置信层。

- 新增整理一组 **南航官方 API 与多组文章型官方分数源**：
  - 南京航空航天大学官方招生计划接口：
    - 计划源：`https://zsservice.nuaa.edu.cn/zsw-admin/api/getEnrollmentPlan`
    - 页面入口：`https://zs.nuaa.edu.cn/zsjh/list.htm`
    - 已抽出：
      - [nanhang_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/nanhang_guangxi_plan_rows.csv:1) `21` 行 `2025` 广西物理类计划
    - 价值：补出广西 `2025` 物理类招生计划，和前面已经登记的分数接口一起，形成“计划 + 专业分 + 学校级概况”完整官方 API 组合。
  - 南京航空航天大学官方 API：
    - 分数源：`https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScore`
    - 概况源：`https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScoreOverview`
    - 已抽出：
      - [nanhang_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/nanhang_guangxi_score_rows.csv:1) `19` 行 `2024-2025` 物理类专业分
      - [nanhang_guangxi_score_overview_rows.csv](/Users/don/Documents/New%20project/reports/nanhang_guangxi_score_overview_rows.csv:1) `4` 行学校级概况
    - 价值：补出广西物理类专业分与学校级录取概况，适合做校级趋势和专业分并行参照。
  - 广西大学官方区内录取统计表：
    - 来源：`https://zs.gxu.edu.cn/info/1277/1968.htm`
    - 已整理：
      - [gxu_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/gxu_guangxi_score_rows.csv:1) `6` 行
    - 价值：补出区内工程向与专项物理类官方行。
  - 北京邮电大学官方广西专业分页：
    - 来源：`https://zsb.bupt.edu.cn/info/1088/2198.htm`
    - 已整理：
      - [bupt_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/bupt_guangxi_score_rows.csv:1) `11` 行
    - 价值：补出广西 `2023` 各专业理工类明细。
  - 苏州大学官方各省录取汇总页：
    - 来源样例：`https://zsb.suda.edu.cn/view.aspx?id=2779`
    - 已整理：
      - [suda_guangxi_score_summary_rows.csv](/Users/don/Documents/New%20project/reports/suda_guangxi_score_summary_rows.csv:1) `3` 行
    - 价值：补出 `2021/2022/2024` 广西理工类学校级摘要。
  - 太原理工大学官方 PDF 摘要：
    - 来源：`https://zs.tyut.edu.cn/__local/4/39/2E/BC13AA04709A12EC9E1B3969035_9F7CAEAF_2702F.pdf`
    - 已整理：
      - [tyut_guangxi_score_summary_rows.csv](/Users/don/Documents/New%20project/reports/tyut_guangxi_score_summary_rows.csv:1) `1` 行
    - 价值：补出 `2021` 广西理工类学校级录取摘要。
  - 太原理工大学官方广西招生计划 PDF：
    - `2025`：`https://zs.tyut.edu.cn/__local/6/E5/19/5342DA63DCE08172C70CE96D984_14FAE149_3B6B9.pdf`
    - `2024`：`https://zs.tyut.edu.cn/__local/E/1F/A4/6E74CAF41F36BB48C39E95CBA7E_019BCA19_3B2AF.pdf`
    - 已整理：
      - [tyut_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/tyut_guangxi_plan_rows.csv:1) `25` 行 `2024-2025` 广西物理类计划
    - 价值：把太原理工这条从“只有早年摘要”补成“摘要 + 近两年计划”的官方 PDF 组合源，覆盖专业计划数和选科要求。

- 新增整理一组 **郑州大学官方广西计划 / 录取页来源**：
  - 广西招生计划页：
    - 入口页：`https://ao.zzu.edu.cn/xxgk/zsjh_/gx/a2025.htm`
    - 官方 PDF：`https://ao.zzu.edu.cn/__local/B/26/EB/BA1AA1F04FE2D060489EB73C48F_613A53AF_E94F.pdf`
    - 已整理：
      - [zzu_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/zzu_guangxi_plan_rows.csv:1) `24` 行 `2025` 广西物理类计划
  - 广西历年录取页：
    - `2025`：`https://ao.zzu.edu.cn/xxgk/lnlq/gx/a2025.htm`
    - `2024`：`https://ao.zzu.edu.cn/xxgk/lnlq/gx/a2024.htm`
    - 已整理：
      - [zzu_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/zzu_guangxi_score_rows.csv:1) `54` 行 `2024-2025` 广西物理类专业分
  - 价值：补出一条新的官方“计划 PDF + 录取页”组合源，既有 `2025` 广西计划，也有 `2024-2025` 广西物理类专业分，覆盖主校区、选科要求、收费标准和最低位次字段。

- 新增整理一组 **西南交通大学官方广西计划 / 录取页来源**：
  - 广西招生计划页：
    - `2025`：`https://cjcx.swjtu.edu.cn/plan/plan_gx_2025.html`
    - `2024`：`https://cjcx.swjtu.edu.cn/plan/plan_gx_2024.html`
    - 已整理：
      - [xinan_jiaoda_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/xinan_jiaoda_guangxi_plan_rows.csv:1) `84` 行 `2024-2025` 广西物理类计划
  - 广西录取页：
    - `2025`：`https://cjcx.swjtu.edu.cn/admission/admission_2025_ANXIZHUANGZUZIZHIOU.html`
    - `2024`：`https://cjcx.swjtu.edu.cn/admission/admission_2024_ANXIZHUANGZUZIZHIOU.html`
    - 已整理：
      - [xinan_jiaoda_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/xinan_jiaoda_guangxi_score_rows.csv:1) `81` 行 `2024-2025` 广西物理类专业分
  - 价值：补出一条新的官方“计划页 + 录取页”组合源，覆盖 `2024-2025` 两年广西物理类计划和专业分；结果里还保留了校区、录取数、平均分和最低位次字段，适合直接用于主口径比较。

- 新增补齐一条 **西南交通大学 2019 官方招生章程基线**：
  - [西南交通大学2019年全日制普通本科招生章程](https://infpub.swjtu.edu.cn/info/1032/1095.htm) `2019/06/21 14:21:09`
  - 来源：西南交通大学信息公开网（来源栏显示：`办公室`）
  - 正文明确进入“第二章 招生计划”，写到学校根据社会经济发展需要、办学条件、生源情况等因素确定分省分专业招生计划编制原则和办法。
  - 价值：
    1. 给西南交通大学补出一条带精确日期的学校侧章程基线。
    2. 让已登记的 `2024-2025` 广西计划页 / 录取页，不再只是结果页，而是能回挂到更早的学校侧招生规则正文。
    3. 后续如果继续比较 `2026` 入口或章程变化，这条 `2019` 官方正文能提供更长的时间参照。

- 新增补齐一条 **西南交通大学 2020 官方招生章程基线**：
  - [西南交通大学2020年全日制普通本科招生章程](https://infpub.swjtu.edu.cn/info/1032/1924.htm) `2021/06/21 14:04:52`
  - 来源：西南交通大学信息公开网（来源栏显示：`办公室`）
  - 正文明确进入“第二章 招生计划”，写到学校确定分省（区、市）分专业招生计划（招生来源计划）编制原则和办法。
  - 正文还明确学校本科招生网为：`https://zhaosheng.swjtu.edu.cn`
  - 价值：
    1. 把西南交通大学学校侧章程基线从单点 `2019` 扩成 `2019 + 2020` 连续时间线。
    2. 让已登记的 `2024-2025` 广西计划页 / 录取页能够回挂到更完整的学校侧规则正文序列。
    3. 为后续比较 `2026` 学校侧入口和规则变化增加一个中间年份参照。

- 新增整理一组 **北京工业大学 / 东华大学官方来源**：
  - 北京工业大学官方计划 PDF：
    - 来源：`https://admissions.bjut.edu.cn/dfiles/2025/2025gaigeshengfenjh.pdf`
    - 已整理：
      - [bjut_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/bjut_guangxi_plan_rows.csv:1) 当前合并视图 `34` 行，其中本轮新抽出 `2025` 广西物理类计划 `16` 行
    - 价值：补出广西 `2025` 物理类分省分专业计划。
  - 北京工业大学官方分数 PDF：
    - 来源：`https://admissions.bjut.edu.cn/lnlqfs/1776.htm`
    - 已整理：
      - [bjut_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/bjut_guangxi_score_rows.csv:1) `17` 行
    - 价值：补出广西 `2025` 物理类专业分，并带普通类平均分备注。
  - 东华大学官方录取分数文章：
    - 来源：`http://zs.dhu.edu.cn/2026/0227/c25199a371750/page.htm`
    - 已整理：
      - [dhu_guangxi_score_rows.csv](/Users/don/Documents/New%20project/reports/dhu_guangxi_score_rows.csv:1) `17` 行
    - 价值：补出广西 `2025` 物化组专业分，覆盖 `物化1` 与 `物化2` 两组。

- 新增整理一组 **中国地质大学（北京）官方 AJAX 来源**：
  - 招生计划入口页：
    - `https://zhsh.cugb.edu.cn/static/front/cugb/basic/html/web/zsjh.html`
    - 页面脚本暴露正式端点：`https://zhsh.cugb.edu.cn/f/ajax_zsjh`
  - 历年分数入口页：
    - `https://zhsh.cugb.edu.cn/static/front/cugb/basic/html/web/lnfs.html`
    - 页面脚本暴露正式端点：`https://zhsh.cugb.edu.cn/f/ajax_lnfs`
  - 已整理：
    - [cugb_beijing_guangxi_plan_rows.csv](/Users/don/Documents/New%20project/reports/cugb_beijing_guangxi_plan_rows.csv:1) `44` 行 `2024-2025` 广西物理类计划
    - [cugb_beijing_guangxi_score_summary_rows.csv](/Users/don/Documents/New%20project/reports/cugb_beijing_guangxi_score_summary_rows.csv:1) `1` 行 `2024` 广西物理类学校级摘要
    - [cugb_beijing_guangxi_score_major_rows.csv](/Users/don/Documents/New%20project/reports/cugb_beijing_guangxi_score_major_rows.csv:1) `9` 行 `2024-2025` 广西物理类专业分
  - 价值：补出一条新的可复用 AJAX 家族官方源，既有计划也有分数；而且能直接保留选科要求、专业备注和位次字段，适合作为后续同族学校横向复制的成功样板。

- 新增整理一个 **江南大学官方招生章程正文页**：
  - [江南大学2025年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2713.htm) `2025-05-30`
  - 来源：江南大学本科招生网
  - 页面内同时给出官方查询系统入口：
    - 招生计划：`http://admission3.jiangnan.edu.cn/pc/recruitstudents/plan`
    - 历年分数：`http://admission3.jiangnan.edu.cn/pc/historyScore/nonArt`
  - 价值：虽然江南大学前端 JS 暴露的计划/分数接口回放还没有跑通，但这条正文页已经把目标校 `2025` 章程基线和后续计划/分数系统入口一起钉住了，适合作为后续服务器侧补抓的稳定起点。

- 新增整理一个 **东北林业大学官方招生计划正文页**：
  - [东北林业大学2025年招生计划](http://zhaosheng.nefu.edu.cn/info/1008/4534.htm) `2025-06-25`
  - 来源：东北林业大学本科招生信息网
  - 正文直接给出官方招生计划查询系统入口：
    - `http://zhaoshengcx.nefu.edu.cn/static/front/nefu/basic/html_web/zsjh.html`
  - 价值：把东北林业大学这条从“只有静态计划页模板缓存”推进到“有发布日期明确的官方正文入口锚点”，后续如果要在服务器侧补抓分省分专业计划，可以优先从这条正文页回溯。

- 新增整理一组 **东北林业大学 / 哈尔滨工程大学章程基线**：
  - [东北林业大学2025年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/4501.htm) `2025-05-29`
    - 来源：`http://zhaosheng.nefu.edu.cn/zszc.htm`
    - 价值：项目缓存里的官方章程列表页已经给出 `2025` 正文章程直链，可用于补目标校 `2025` 章程基线。
  - [哈尔滨工程大学2024年本科招生章程](https://zsb.hrbeu.edu.cn/f/newsCenter/article/8c9628810bb24cb98bc510652463df73) `2024-05-24`
    - 来源：哈尔滨工程大学本科招生网
    - 正文页导航同时锚定官方系统入口：
      - 招生计划：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/zsjh.html`
      - 历年分数：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html`
    - 价值：虽然当前缓存里还没有哈工程 `2025` 普通本科章程正文，但这条 `2024` 官方章程页已经把目标校章程基线和后续系统入口钉住了，可作为后续服务器侧追 `2025/2026` 变化时的稳定参照。

- 新增补齐一组 **哈尔滨工程大学历史章程基线**：
  - [哈尔滨工程大学2023年本科招生章程](https://zsb.hrbeu.edu.cn/f/newsCenter/article/9c20c71a63624ec6a3afd2d50dac4f2d) `2023-06-02`
    - 来源：哈尔滨工程大学本科招生网
    - 正文页导航同样锚定官方系统入口：
      - 招生计划：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/zsjh.html`
      - 历年分数：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html`
  - [哈尔滨工程大学2022年本科招生章程](https://zsb.hrbeu.edu.cn/f/newsCenter/article/3bb44b3c453e4ac8ae3be089fd02311d) `2022-05-27`
    - 来源：哈尔滨工程大学本科招生网
    - 正文页导航同样锚定官方系统入口：
      - 招生计划：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/zsjh.html`
      - 历年分数：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html`
  - [哈尔滨工程大学2021年本科招生章程](https://zsb.hrbeu.edu.cn/f/newsCenter/article/8ca03576369041e4af394dbaa89e15e9) `2021-05-12`
    - 来源：哈尔滨工程大学本科招生网
    - 正文页导航同样锚定官方系统入口：
      - 招生计划：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/zsjh.html`
      - 历年分数：`https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html`
  - 价值：把哈工程这条从“只有单年章程基线”推进到“连续多年章程时间序列基线”；后续如果要追 `2025/2026` 入口或章程变化，现在已经有 `2021-2024` 的本地官方参照。

- 新增把 **哈尔滨工程大学学校侧 query chain** 从“同家族接口疑似 403”升级为“计划 + 分数 API 已打通”的口径：
  - 学校侧入口模板：
    - `https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html/web/zsjh.html`
    - `https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html/web/lnfs.html`
  - `2026-05-18` 服务器侧新增验证：
    1. 继续抓取 live `https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/js/tplt.js` 后，已确认哈尔滨工程大学与 USTB / 云南大学同族，真实前端顺序是先 `POST /f/ajax_get_csrfToken (n=3)`，再把返回 token 串拆分后轮转写入 `Csrf-Token` 请求头；
    2. 虽然旧静态壳页 `zsjh.html` 本身当前返回 `404`，但同站 `POST https://zsb.hrbeu.edu.cn/f/ajax_get_csrfToken` 仍成功返回 `200` 和 token 串，随后 `f/ajax_zsjh_param` 与 `f/ajax_lnfs_param` 也都成功返回 `200` 和完整参数表；
    3. 继续定向回放 `广西 + 2025 + 物理类/历史类 + 普通类` 后，计划链 `f/ajax_zsjh` 与分数链 `f/ajax_lnfs` 都成功直返正式数据：
       - 计划侧：`物理类` 总计划 `56`、专业行 `16` 条；`历史类` 总计划 `7`、专业行 `4` 条；
       - 分数侧：`物理类` 最低分 `602`、最低位次 `5982`、平均分 `607`、最高分 `622`、专业行 `16` 条；`历史类` 最低分 `557`、最低位次 `5253`、平均分 `569`、最高分 `585`、专业行 `4` 条。
    4. 参数响应、四份原始 JSON 与两份合并 CSV 已缓存到：
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_zsjh_param.json`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_guangxi_wuli_plan.json`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_guangxi_lishi_plan.json`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_guangxi_plan_rows.csv`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_lnfs_param.json`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_guangxi_wuli_score.json`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_guangxi_lishi_score.json`
       - `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2025_guangxi_score_rows.csv`
  - 价值：
    1. 这把哈尔滨工程大学从“规则基线已齐但 query family 仍像阻塞”的状态，直接升级成“学校侧广西计划 + 分数 API 已落地”的实数源。
    2. 也说明这类同族站点不能仅根据旧静态壳页是否 `404` 来判死，关键还是要看 `tplt.js` 暴露的真实 `csrf` 链是否仍然可用。
    3. 后续更值得继续回推哈尔滨工程大学 `2024-2023` 广西计划 / 分数及 `国家专项`，而不是再把它当成单纯的 403 / 404 阻塞站点处理。
    4. `2026-05-18` 同轮继续沿完全相同的 token 链往前回推后，又确认了哈尔滨工程大学 `2024` 与 `2023` 的广西分数时间线：
       - `2024` 广西 `普通类`：`物理类` 最低分 `607`、最低位次 `5931`、专业行 `12` 条；`历史类` 最低分 `575`、最低位次 `3263`、专业行 `3` 条；
       - `2024` 广西 `国家专项`：`物理类` 最低分 `568`、最低位次 `17775`、专业行 `3` 条；
       - `2023` 广西 `普通类`：`理工` 最低分 `586`、最低位次 `7458`、专业行 `13` 条；`文史` 最低分 `582`、最低位次 `2875`、专业行 `3` 条；
       - `2023` 广西 `国家专项`：`理工` 最低分 `541`、最低位次 `18736`、专业行 `3` 条。
       对应原始 JSON 与跨年汇总 CSV 已缓存到 `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_2024_guangxi_wuli_score.json`、`hrbeu_2024_guangxi_lishi_score.json`、`hrbeu_2024_guangxi_wuli_national_special_score.json`、`hrbeu_2023_guangxi_ligong_score.json`、`hrbeu_2023_guangxi_wenshi_score.json`、`hrbeu_2023_guangxi_ligong_national_special_score.json` 与 `hrbeu_2023_2024_guangxi_score_rows.csv`。
    5. 同轮再沿 live `zsjh_param` 做最低成本复核后，已确认哈尔滨工程大学这条计划链和分数链并不对称：广西参数映射里只出现 `2025` 年度组合，
       - `广西_2025_物理类`：`普通类 / 国家专项 / 少数民族预科`
       - `广西_2025_历史类`：`普通类`
       而继续按完全同一条 token 链回放 `2024` 与 `2023` 的广西 `普通类` 计划请求时，接口虽仍返回 `state=1 / msg=操作成功`，但 `zsjhTotal` 与 `zsjhList` 都为空。对应 live 参数 JSON 已缓存到 `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_live_zsjh_param_20260518.json`。
    6. 这说明哈尔滨工程大学学校侧分数链确实可以回推到 `2023-2025`，但广西计划链当前只公开到 `2025`；因此后续不该再反复重试 `2024/2023` 广西计划，而应把精力放到更早分数扩展或其它学校的计划链上。
    7. `2026-05-18` 再沿完全相同的 `lnfs` 真链补抓参数表中尚未落地的广西 `国家专项 / 少数民族预科` 组合后，又新增命中：
       - `2025` 广西 `国家专项`：`物理类` 录取人数 `8`、最低分 `582`、最低位次 `11543`、平均分 `585`、最高分 `590`、专业行 `4` 条；
       - `2025` 广西 `少数民族预科`：`物理类` 录取人数 `8`、最低分 `590`、最低位次 `9017`、平均分 `592`、最高分 `595`、专业行 `1` 条；
       - `2024` 广西 `少数民族预科`：`物理类` 录取人数 `8`、最低分 `585`、最低位次 `11643`、平均分 `589.62`、最高分 `596`、专业行 `1` 条；
       - `2023` 广西 `少数民族预科`：`理工` 录取人数 `6`、最低分 `533`、最低位次 `21553`、平均分 `543.17`、最高分 `553`、专业行 `1` 条；`文史` 录取人数 `2`、最低分 `557`、最低位次 `6180`、平均分 `568`、最高分 `579`、专业行 `1` 条。
       新增原始 JSON、行级 CSV 与跨年少数民族预科汇总 CSV 已缓存到 `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_20250518_extra_score_bundle.json`、`hrbeu_2025_guangxi_wuli_national_special_score.json`、`hrbeu_2025_guangxi_wuli_national_special_score_rows.csv`、`hrbeu_2025_guangxi_wuli_minority_prep_score.json`、`hrbeu_2025_guangxi_wuli_minority_prep_score_rows.csv`、`hrbeu_2024_guangxi_wuli_minority_prep_score.json`、`hrbeu_2024_guangxi_wuli_minority_prep_score_rows.csv`、`hrbeu_2023_guangxi_ligong_minority_prep_score.json`、`hrbeu_2023_guangxi_ligong_minority_prep_score_rows.csv`、`hrbeu_2023_guangxi_wenshi_minority_prep_score.json`、`hrbeu_2023_guangxi_wenshi_minority_prep_score_rows.csv` 与 `hrbeu_2023_2025_guangxi_minority_prep_score_rows.csv`。
    8. 这把哈工程广西分数链从原来的“普通类 + 零散国家专项”继续推进成“普通类 + 国家专项 + 少数民族预科”三条并行子线，也再次说明这类同族站点即使旧静态壳页 `404`，只要 `csrf + X-Requested-Time + token 轮转` 仍可复现，学校侧细分批类数据就仍然值得继续低成本深挖。
    9. `2026-05-18` 同轮再沿完全相同的 `zsjh` 真链补抓参数表里已公开但尚未落表的广西专项计划组合后，又新增命中：
       - `2025` 广西 `国家专项`：`物理类` 总计划 `8`、专业行 `4` 条，分别为 `能源动力类`、`机械类`、`新能源材料与器件`、`核化工与核燃料工程`；
       - `2025` 广西 `少数民族预科`：`物理类` 总计划 `8`、专业行 `1` 条（`少数民族预科`，学制 `一年`）。
       对应原始 JSON 与行级 CSV 已缓存到 `raw_data/official_followup/haerbin_gongcheng_211/hrbeu_20250518_extra_plan_bundle.json`、`hrbeu_2025_guangxi_wuli_national_special_plan.json`、`hrbeu_2025_guangxi_wuli_national_special_plan_rows.csv`、`hrbeu_2025_guangxi_wuli_minority_prep_plan.json` 与 `hrbeu_2025_guangxi_wuli_minority_prep_plan_rows.csv`。
    10. 这把哈工程从“普通类计划 + 三条分数子线”进一步推进到“普通类计划 + 国家专项计划 + 少数民族预科计划”也开始分类型落地，学校侧广西计划链的结构完整度明显提高。

- 新增整理一组 **目标校官方招生章程正文链接**：
  - [中国传媒大学2025年本科招生章程](https://zhaosheng.cuc.edu.cn/2025/0530/c5852a256319/page.htm) `2025-05-30`
    - 来源：`https://zhaosheng.cuc.edu.cn/zszc/list.htm`
    - 价值：项目缓存里虽暂时只有官方章程列表页，但列表已经给出 `2025` 正文章程的精确标题、日期和直达链接，可用于补目标校章程基线。
  - [海南大学2025年本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/5087.htm) `2025-05-28`
    - 来源：`https://bkzs.hainanu.edu.cn/zsxx/zszc.htm`
    - 同页还锚定了官方系统入口：
      - 招生计划：`https://zsfw.hainanu.edu.cn/static/front/hainanu/basic/html_web/zsjh.html`
      - 历年分数：`https://zsfw.hainanu.edu.cn/static/front/hainanu/basic/html_web/lnfs.html`
    - 价值：把海南大学这条从“只有章程栏目页和静态模板页缓存”推进到“有 `2025` 正文章程直链和系统入口锚点”，适合作为后续服务器侧补抓的起点。

- 新增整理一组 **大连海事大学官方正文页**：
  - [大连海事大学2025年本科招生章程](https://bkzs.dlmu.edu.cn/info/1018/2719.htm) `2025-05-29`
    - 来源：大连海事大学本科招生网
    - 正文页导航同时锚定官方系统入口：
      - 招生计划：`https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html_web/zsjh.html`
      - 历年分数：`https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html_web/lnfs.html`
      - 录取查询：`https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html_web/lqcx.html`
  - [向海而行｜2025年分省分专业招生计划发布！](https://bkzs.dlmu.edu.cn/info/1017/2809.htm) `2025-06-16`
    - 来源：大连海事大学本科招生网
    - 正文明确宣布 `2025` 分省分专业招生计划正式发布，并回指官方计划查询系统。
  - 价值：把大连海事这条从“同族 AJAX 模板页可见但接口被拒”推进到“有章程正文和计划发布正文双锚点”，后续如果要在服务器侧换角度补抓分省分专业计划，可以优先沿这两个官方正文页回溯。

- 新增整理一个 **中国石油大学（北京）官方本科招生入口页**：
  - [本科招生](https://www.cup.edu.cn/dbewm/8cd0dc4a2eec46129adf843b29b6571f.htm) `2023-03-09`
  - 来源：中国石油大学（北京）官网
  - 页内明确指向本科招生入口：
    - `http://bkzs.cup.edu.cn/f`
  - 价值：虽然中国石油大学（北京）招生站的同族 AJAX 接口当前仍是 `403`，但这条学校主站入口页把“官方本科招生入口在哪里”这件事钉住了，能补 `目标校招生入口变化` 这类缺口，也适合作为后续服务器侧换角度补抓时的回溯起点。

- 新增整理一个 **北京科技大学官方报考指南入口页**：
  - [北京科技大学本科招生网报考指南](https://zhaosheng.ustb.edu.cn/zkxx/bkzn/43d4c16e4c7f4fe282712a08f0b4699e.htm) `2021-06-18`
  - 来源：北京科技大学本科招生网
  - 同页导航明确锚定官方系统入口：
    - 招生计划：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/zsjh.html`
    - 历年分数：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/lnfs.html`
    - 录取查询：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/lqcx.html`
  - 价值：虽然北京科技大学这条同族 AJAX 接口当前仍是显式 `403`，但这页把官方报考指南与计划/分数/录取查询入口一起钉住了，适合作为后续服务器侧换角度补抓的稳定起点。

- 新增补齐一组 **目标校 2025 官方招生章程基线**：
  - [南京航空航天大学2025年本科招生章程](https://zs.nuaa.edu.cn/2025/0530/c9155a376532/page.htm) `2025-05-30`
    - 来源：南京航空航天大学本科招生网
    - 正文页导航同时覆盖 `分省指南` 与 `报考指南` 栏目。
  - [西安电子科技大学2025年本科招生章程](https://zsb.xidian.edu.cn/info/1009/5963.htm) `2025-05-29`
    - 来源：西安电子科技大学本科招生信息网
    - 正文明确录取结果与招生信息查询均以学校招生信息网 `https://zsb.xidian.edu.cn` 为准。
  - [华东理工大学2025年本科招生章程](https://zsb.ecust.edu.cn/2025/0529/c2307a179246/page.htm) `2025-05-29`
    - 来源：华东理工大学本科招生网
  - [东华大学2025年本科招生章程](http://zs.dhu.edu.cn/2025/0522/c9563a361995/page.htm) `2025-05-22`
    - 来源：东华大学本科招生网
  - [上海大学2025年本科招生章程](https://bkzsw.shu.edu.cn/info/7563/37700.htm) `2025年05月30日 16:00`
    - 来源：上海大学本科招生网
    - 正文同时明确学校本科招生网址为 `https://bkzsw.shu.edu.cn`。
  - 价值：这批学校此前已经在项目里补出了广西计划 / 分数接口或正文页，但 `2025` 章程基线还没系统登记；本轮补齐后，后续追 `2026` 章程变化时会更容易做逐校对比。

- 新增补齐一组 **更多目标校 2025 章程基线**：
  - [太原理工大学2025年本科招生章程](http://zs.tyut.edu.cn/info/1006/4687.htm) `2025-05-15`
    - 来源：太原理工大学本科招生网
    - 正文页导航同时锚定官方招生计划入口：`https://zhaolu.zjzw.cn/release-page/plan?key=87d44f0fdd975fdba3aab7bc`
  - [武汉理工大学2025年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202505/t20250530_1331279.shtml) `2025-05-30`
    - 来源：`https://zs.whut.edu.cn/zc/zszc/`
    - 同页导航同时锚定：
      - 招生计划：`https://zs.whut.edu.cn/bkcx/bkzsjh/`
      - 历年分数：`https://zs.whut.edu.cn/bkcx/bklqqk/`
      - 录取查询：`https://lqcx.whut.edu.cn/`
  - [郑州大学2025年本科招生章程](http://ao.zzu.edu.cn/info/1793/4894.htm) `2025-05-22`
    - 来源：`http://ao.zzu.edu.cn/xxgk/zszc.htm`
    - 同页导航同时锚定：
      - 招生计划：`http://ao.zzu.edu.cn/xxgk/zsjh_.htm`

- 新增补齐一条 **太原理工大学 2024 官方招生章程基线**：
  - [太原理工大学2024年本科招生章程](http://zs.tyut.edu.cn/info/1006/2927.htm) `2024-05-21`
  - 来源：太原理工大学本科招生网
  - 正文页导航同时锚定官方招生计划入口：
    - `https://zhaolu.zjzw.cn/release-page/plan?key=87d44f0fdd975fdba3aab7bc`
  - 正文明确学校本科招生网址为：
    - `http://zs.tyut.edu.cn`
  - 同校已在项目中登记的官方基线：
    - [太原理工大学2025年本科招生章程](http://zs.tyut.edu.cn/info/1006/4687.htm) `2025-05-15`
    - [太原理工大学广西招生计划 PDF（2024-2025 物理类计划）](https://zs.tyut.edu.cn/__local/6/E5/19/5342DA63DCE08172C70CE96D984_14FAE149_3B6B9.pdf)
  - 价值：
    1. 把太原理工大学从“只有 `2025` 章程基线”推进到“`2024` + `2025` 连续章程基线”。
    2. 让章程正文、计划入口和已登记的广西计划 PDF 形成更完整的学校侧时间线。
    3. 为后续比较 `2026` 学校侧入口与条文变化提供更稳的上年参照。
      - 历年录取：`http://ao.zzu.edu.cn/xxgk/lnlq_.htm`
  - 价值：这三校此前已经在项目里有广西计划 / 分数正文或结构化结果，但章程基线尚未正式登记；本轮补齐后，后续做 `2026` 章程与入口变化比对时，学校侧基线更完整了。

- 新增补齐一条 **长安大学 2025 官方招生章程基线**：
  - [长安大学2025年本科招生章程](https://zsb.chd.edu.cn/info/1018/1069.htm) `2025.06.05`
  - 来源：长安大学本科招生网
  - 正文页导航同时锚定官方系统入口：
    - 招生计划：`https://zsdata.chd.edu.cn/zsdata/lqxx/#/`
    - 历年分数：`https://zsdata.chd.edu.cn/zsdata/lqxx/#/lnfs`
    - 录取查询：`https://zsdata.chd.edu.cn/zsdata/lqxx/#/lqcx`
  - 价值：
    1. 补齐目标校 `2025` 官方章程基线。
    2. 反向锚定了项目里已登记的长安大学官方 `LQXX` 计划 / 分数接口来源。
    3. 为后续对比 `2026` 章程变化与继续服务器侧补抓提供稳定主站入口。

- 新增补齐一条 **北京科技大学 2025 官方招生章程基线**：
  - [北京科技大学2025年本科招生章程](https://zhaosheng.ustb.edu.cn/zkxx/zszc/fc4aa12fb8254e97b9ee7a405f57cb8b.htm) `2025-06-04`
  - 来源：北京科技大学本科招生网
  - 章程栏目页也已在缓存中明确给出同一条目：
    - `https://zhaosheng.ustb.edu.cn/zkxx/zszc/index.htm`
  - 正文页 / 栏目页共同锚定官方系统入口：
    - 招生计划：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/zsjh.html`
    - 历年分数：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/lnfs.html`
    - 录取查询：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/lqcx.html`
  - 价值：
    1. 把北科大从“只有报考指南入口锚点”推进到“有 `2025` 正文章程基线”。
    2. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方基线。
    3. 继续强化北科大这条学校侧系统入口链路，方便后续服务器侧换角度补抓。

- 新增补齐一条 **北京交通大学 2025 官方招生章程基线**：
  - [北京交通大学2025年招生章程](http://zsw.bjtu.edu.cn/f/newsCenter/article/5cc220a8189e408a929281c20c3e4ee5) `2025-05-29`
  - 来源：北京交通大学本科招生网
  - 正文页导航同时锚定官方系统入口：
    - 招生计划：`http://zsw.bjtu.edu.cn/zsw/zsjh.html`
    - 历年分数：`http://zsw.bjtu.edu.cn/zsw/lnfs.html`
  - 价值：
    1. 补齐北京交通大学 `2025` 官方章程基线。
    2. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。
    3. 反向锚定了项目里已登记的北交大隐藏 JSON 计划 / 分数来源，补全“章程 + 数据源”这条学校侧链路。

- 新增补齐一条 **南京农业大学 2025 官方招生章程基线**：
  - [南京农业大学2025年本科招生章程](http://zsxx.njau.edu.cn/info/1016/4062.htm) `2025-05-30`
  - 来源：南京农业大学本科招生网
  - 章程正文明确写到：分省分专业招生计划可登录南京农业大学本科招生网站查询。
  - 项目缓存中已同步存在官方招生计划页：
    - `https://njauzsb.njau.edu.cn/zsw/zsjh.html`
  - 价值：
    1. 补齐南京农业大学 `2025` 官方章程基线。
    2. 把章程正文与官方计划查询页正式绑在一起，方便后续服务器侧继续补抓。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **宁夏大学 2025 官方招生章程基线**：
  - [宁夏大学2025年普通本科招生章程](http://zs.nxu.edu.cn/info/1021/3248.htm) `2025年06月04日`
  - 来源：宁夏大学本科招生网招生章程栏目页
    - 栏目页：`http://zs.nxu.edu.cn/zsxx/zszc.htm`
  - 同批缓存中已同步存在官方系统入口：
    - 招生计划：`http://zscx.nxu.edu.cn/zsw/zsjh.html`
    - 历年分数：`http://zscx.nxu.edu.cn/zsw/lnfs.html`
    - 录取进程：`http://zscx.nxu.edu.cn/zsw/lqjc.html`
    - 录取结果：`http://zscx.nxu.edu.cn/zsw/lqcx.html`
  - 价值：
    1. 补齐宁夏大学 `2025` 官方章程基线。
    2. 把章程栏目页与计划 / 分数 / 录取查询系统入口正式绑在一起，方便后续服务器侧继续补抓。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐两条 **宁夏大学上年官方招生章程基线**：
  - [宁夏大学2024年普通本科招生章程](http://zs.nxu.edu.cn/info/1021/3133.htm) `2024年05月13日`
  - [宁夏大学2023年普通本科招生章程](http://zs.nxu.edu.cn/info/1021/2851.htm) `2023年06月09日`
  - 来源：宁夏大学本科招生网招生章程栏目页
    - 栏目页：`http://zs.nxu.edu.cn/zsxx/zszc.htm`
  - 同一栏目页同时锚定官方系统入口：
    - 招生计划：`http://zscx.nxu.edu.cn/zsw/zsjh.html`
    - 历年分数：`http://zscx.nxu.edu.cn/zsw/lnfs.html`
    - 录取进程：`http://zscx.nxu.edu.cn/zsw/lqjc.html`
    - 录取结果：`http://zscx.nxu.edu.cn/zsw/lqcx.html`
  - 价值：
    1. 把宁夏大学从“只有 `2025` 章程基线”推进到“`2023` + `2024` + `2025` 连续章程基线”。
    2. 让宁夏大学学校侧章程时间线和计划 / 分数 / 录取查询系统入口形成更完整的上年参照。
    3. 为后续比较 `2026` 学校侧入口与条文变化提供连续官方时间线。

- 新增补齐一条 **贵州大学 2025 官方招生章程基线**：
  - [贵州大学2025年本科招生章程](https://rso.gzu.edu.cn/2025/0513/c17366a250006/page.htm) `2025-05-13`
  - 来源：贵州大学本科招生网
  - 正文页导航同时锚定官方系统入口：
    - 招生计划：`https://rso.gzu.edu.cn/zsjh_17370/list.htm`
    - 录取查询：`https://rso.gzu.edu.cn/lqcx/list.htm`
  - 项目缓存中已同步存在官方计划正文页：
    - [贵州大学2025年普通本科招生计划（含国家专项、地方专项）](https://rso.gzu.edu.cn/2025/0620/c17370a252806/page.htm) `2025-06-20`
  - 价值：
    1. 补齐贵州大学 `2025` 官方章程基线。
    2. 把章程正文与官方计划页、录取查询入口正式绑在一起，方便后续服务器侧继续补抓。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **西北大学 2025 官方招生计划基线**：
  - [西北大学2025年本科招生计划](https://zsb.nwu.edu.cn/info/1049/2984.htm) `2025/06/25`
  - 来源：西北大学本科生招生信息网
  - 正文提供官方附件：
    - `西北大学2025年本科招生计划表.pdf`
  - 同页导航同时锚定官方入口：
    - 历年分数查询：`http://zhinengdayi.com/page/detail/FCHTWR/2464/6548`
    - 录取查询：`http://xdzsb.nwu.edu.cn/search_gklq.asp`
    - 招生章程栏目：`https://zsb.nwu.edu.cn/zszn/zszc1.htm`
  - 价值：
    1. 补出西北大学这所目标校的 `2025` 官方计划基线。
    2. 把计划正文、PDF 附件和学校侧分数 / 录取 / 章程入口正式绑在一起。
    3. 为后续继续追西北大学的 `2025-2026` 学校侧变化提供稳定锚点。

- 新增补齐五条 **西北大学上年官方招生计划基线**：
  - [西北大学2024年本科招生计划](https://zsb.nwu.edu.cn/info/1049/2688.htm) `2024/06/20`
    - 附件：`西北大学2024年本科招生计划.pdf`
  - [西北大学2023年本科招生计划](https://zsb.nwu.edu.cn/info/1049/2471.htm) `2023/06/18`
    - 附件：`西北大学2023年本科招生计划.pdf`
  - [西北大学2022年本科招生计划](https://zsb.nwu.edu.cn/info/1049/2203.htm) `2022/06/17`
    - 附件：`西北大学2022年本科招生计划.pdf`
  - [西北大学2021年本科招生计划](https://zsb.nwu.edu.cn/info/1049/1882.htm) `2021/06/17`
    - 附件：`西北大学2021年本科招生计划.pdf`
  - [西北大学2020年本科招生计划](https://zsb.nwu.edu.cn/info/1049/1677.htm) `2020/07/17`
  - 来源：西北大学本科生招生信息网
  - 这些正文页与 `2025` 计划页属于同一学校侧计划发布链路；其中 `2021-2024` 均挂出官方 PDF 附件，`2020` 为图文正文页。
  - 价值：
    1. 把西北大学从“只有 `2025` 计划基线”推进到“`2020-2025` 连续计划时间线”。
    2. 这让后续比较学校侧计划发布时间、附件形式和入口变化时，有了连续多年的官方参照。
    3. 也补强了项目里“学校侧正文页 + 附件 PDF”这类可复用计划源的连续年度样本。

- 新增补齐一条 **辽宁大学 2025 官方招生章程基线**：
  - [辽宁大学2025年本科招生章程](http://zs.lnu.edu.cn/info/14170/71533.htm) `2025-05-16 16:58`
  - 来源：辽宁大学本科招生网
  - 正文页导航同时锚定官方系统入口：
    - 招生计划列表：`http://zs.lnu.edu.cn/cxzx/zsjh.htm`
    - 历年录取情况列表：`http://zs.lnu.edu.cn/cxzx/lnlqqk1.htm`
    - 成绩查询：`http://zs.lnu.edu.cn/cxzx/cjcx.htm`
    - 录取结果查询：`http://zs.lnu.edu.cn/cxzx/lqjgcx.htm`
  - 同批缓存中已命中广西直达列表项：
    - `广西壮族自治区2025年招生计划` `2025-06-26`
    - `广西壮族自治区2025年录取情况` `2026-01-13`
  - 价值：
    1. 补齐辽宁大学 `2025` 官方章程基线。
    2. 把章程正文与广西计划 / 录取情况学校侧入口正式绑在一起，方便后续服务器侧继续补抓具体广西页。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **内蒙古大学 2025 官方招生章程基线**：
  - [内蒙古大学2025年本科招生章程](https://zhaosheng.imu.edu.cn/info/1168/2998.htm) `2025-06-06 10:42`
  - 来源：内蒙古大学招生网
  - 正文页导航同时锚定官方学校侧入口：
    - 报考指南：`https://zhaosheng.imu.edu.cn/bkzn/zszc.htm`
    - 分数公示：`https://zhaosheng.imu.edu.cn/fsgs.htm`
    - 录取查询：`https://zhaosheng.imu.edu.cn/xxcx.htm`
  - 正文明确写到：学校分省来源招生计划由各省级招生主管部门向社会公布。
  - 价值：
    1. 补齐内蒙古大学 `2025` 官方章程基线。
    2. 把章程正文与学校侧分数公示、录取查询入口正式绑在一起，方便后续继续追入口变化。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐两条 **内蒙古大学上年官方招生章程基线**：
  - [内蒙古大学2024年本科招生章程](https://zhaosheng.imu.edu.cn/info/1168/2840.htm) `2024-06-05 17:24`
  - [内蒙古大学2023年本科招生章程](https://zhaosheng.imu.edu.cn/info/1085/2677.htm) `2023-06-06 10:30`
  - 来源：内蒙古大学招生网
    - 作者栏：`内大招办`
  - 正文明确写到：
    - 分省来源计划由有关省（自治区、直辖市）招生管理部门按规定方式向社会公布，考生也可以在内蒙古大学招生网查询。
  - 页头导航同时锚定：
    - 报考指南：`https://zhaosheng.imu.edu.cn/bkzn/zszc.htm`
    - 分数公示：`https://zhaosheng.imu.edu.cn/fsgs.htm`
    - 录取查询：`https://zhaosheng.imu.edu.cn/xxcx.htm`
  - 价值：
    1. 把内蒙古大学从“只有 `2025` 章程基线”推进到“`2023` + `2024` + `2025` 连续章程基线”。
    2. 让学校侧章程正文与分数公示、录取查询入口形成更完整的上年参照。
    3. 为后续比较 `2026` 学校侧入口与条文变化提供连续官方时间线。

- 新增补齐一条 **新疆大学 2025 官方招生章程基线**：
  - [新疆大学2025年普通本科招生章程](https://welcome.xju.edu.cn/Web/Home/Detail?w1_V5THB3TJlfCNztg6Yvq0cSSbgBNpRUMVsWpe2c5g=.shtml) `2025-05-06`
  - 来源：新疆大学迎新网
  - 正文明确写到：`2025` 年招生计划及专业按各省级招生考试管理部门公布为准。
  - 当前缓存里这条来源的定位更偏学校侧官方章程基线，而不是完整的计划 / 分数系统入口页。
  - 价值：
    1. 补齐新疆大学 `2025` 官方章程基线。
    2. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。
    3. 把新疆大学从“缓存里已有正文但未登记”推进到正式入账来源。

- 新增补齐一条 **华南师范大学 2025 官方招生章程基线**：
  - [华南师范大学2025年夏季高考招生章程](http://zsb.scnu.edu.cn/a/20250515/684.html) `2025-05-15 10:15:00`
  - 来源：华南师范大学本科招生网
  - 正文同时提供官方 PDF 附件：
    - `华南师范大学2025年夏季普通高考招生章程.pdf`
  - 同站缓存中还存在学校侧栏目入口：
    - 招生计划：`http://zsb.scnu.edu.cn/zhaoshengjihua/`
    - 志愿参考：`http://zsb.scnu.edu.cn/zhiyuancankao/`
  - 价值：
    1. 补齐华南师范大学 `2025` 官方章程基线。
    2. 把章程正文、PDF 附件和学校侧计划 / 志愿参考栏目正式绑在一起。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **西南大学 2025 官方招生章程基线**：
  - [西南大学2025年普通本科招生章程](http://bkzsw.swu.edu.cn/info/1047/1834.htm) `2025-05-29 09:30:45`
  - 来源：西南大学本科招生网
  - 正文明确写到：学校本科招生网址为 `http://bkzsw.swu.edu.cn`。
  - 价值：
    1. 补齐西南大学 `2025` 官方章程基线。
    2. 把章程正文与学校正式本科招生站点锚定起来，方便后续继续追计划 / 分数入口变化。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **西南财经大学 2025 官方招生章程基线**：
  - [西南财经大学2025年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/8321.htm) `2025-05-29`
  - 来源：西南财经大学本科招生网
  - 同批缓存中已确认：
    - 章程栏目页：`https://zb.swufe.edu.cn/zszc1.htm`
    - 官方数据查询入口：`https://zsdata.swufe.edu.cn/zsdata/lqxx.html`
  - 正文明确写到：学校本科招生网址为 `http://zb.swufe.edu.cn/`。
  - 价值：
    1. 补齐西南财经大学 `2025` 官方章程基线。
    2. 把章程正文与学校侧数据查询系统入口正式绑在一起。
    3. 为后续对比 `2026` 章程变化与继续服务器侧补抓提供稳定入口。

- 新增补齐一条 **中国药科大学 2025 官方招生章程基线**：
  - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
  - 来源：中国药科大学本科生招生网
  - 正文页导航同时锚定官方学校侧入口：
    - `2025招生计划`：`http://zb.cpu.edu.cn/gszszn/list.htm`
    - `历年招生计划`：`http://zb.cpu.edu.cn/lnzsjh/list.htm`
    - `历年录取分数`：`http://zb.cpu.edu.cn/fs/list.htm`
    - `高考录取查询`：`http://zb.cpu.edu.cn/gklqcx/list.htm`
  - 价值：
    1. 补齐中国药科大学 `2025` 官方章程基线。
    2. 把章程正文与计划 / 分数 / 录取查询入口正式绑在一起。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **中国药科大学 2024 官方招生章程基线**：
  - [中国药科大学2024年普通本科招生章程](http://zb.cpu.edu.cn/2b/1f/c9133a207647/page.htm) `2024-06-12`
  - 来源：中国药科大学本科生招生网
  - 正文页导航同时锚定官方学校侧入口：
    - 历年招生计划：`http://zb.cpu.edu.cn/lnzsjh/list.htm`
    - 历年录取分数：`http://zb.cpu.edu.cn/fs/list.htm`
    - 高考录取查询：`http://zb.cpu.edu.cn/gklqcx/list.htm`
  - 同校已在项目中登记的官方基线：
    - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
    - [2025年广西招生计划](http://zb.cpu.edu.cn/2d/1d/c12765a208157/page.htm) `2025-06-23`
  - 价值：
    1. 把中国药科大学从“只有 `2025` 章程基线”推进到“`2024` + `2025` 连续章程基线”。
    2. 让学校侧章程正文与历年招生计划 / 历年录取分数 / 高考录取查询入口形成更完整的上年参照。
    3. 为后续比较 `2026` 学校侧入口与条文变化提供明确的连续官方时间线。

- 新增补齐一条 **暨南大学 2025 官方招生章程基线**：
  - [暨南大学2025年本科招生章程](https://zsb.jnu.edu.cn/2025/0530/c40320a837360/page.htm) `2025-05-30`
  - 来源：暨南大学招生办公室
  - 正文明确写到：招生网址为 `https://zsb.jnu.edu.cn`。
  - 同批缓存中已确认学校侧入口：
    - 历年分数：`https://zsb.jnu.edu.cn/2016/1206/c3468a93231/page.psp`
    - 招生计划栏目：`https://zsb.jnu.edu.cn/40329/list.htm`
    - 录取查询：`https://lxlz.jnu.edu.cn/pugao/`
  - 价值：
    1. 补齐暨南大学 `2025` 官方章程基线。
    2. 把章程正文与学校侧计划 / 分数 / 录取查询入口正式绑在一起。
    3. 为后续对比 `2026` 章程变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **暨南大学 2025 官方分省分专业计划基线**：
  - [暨南大学2025年分省分专业招生计划](https://zsb.jnu.edu.cn/2025/0625/c40320a839249/page.htm) `2025-06-26`
  - 来源：暨南大学招生办公室
  - 正文直接挂出各省分省分专业计划子页，其中已明确出现广西子页：
    - `https://zsb.jnu.edu.cn/2025/0624/c4288a839137/page.htm`
  - 正文还明确回指：
    - [暨南大学2025年本科招生章程](https://zsb.jnu.edu.cn/2025/0530/c40320a837360/page.htm)
  - 价值：
    1. 补出暨南大学这所目标校的 `2025` 官方计划基线。
    2. 把计划正文与广西子页入口正式绑在一起，方便后续服务器侧继续补抓具体广西计划明细。
    3. 把“章程 + 计划 + 广西入口”这条学校侧链路补完整了。

- 新增补齐一条 **暨南大学 2023 官方分省分专业计划基线**：
  - [暨南大学2023年分省分专业招生计划](https://zsb.jnu.edu.cn/2023/0608/c3470a755481/page.htm) `2023-06-08`
  - 来源：暨南大学招生办公室
  - 正文直接给出各省分省分专业计划总表，并明确出现：
    - 广西：`100`
  - 正文同时挂出广西子页：
    - `https://zsb.jnu.edu.cn/2023/0608/c4288a755405/page.htm`
  - 价值：
    1. 给暨南大学补出一个可与 `2025` 计划页直接对照的上年官方计划基线。
    2. 把学校侧广西计划入口的年度变化线再往前延伸一年，方便后续比较入口与计划规模变化。
    3. 这条证据完全来自本地已缓存官方正文页，不需要再重复高成本探测。

- 新增补齐一条 **东北师范大学 2025 官方招生章程基线**：
  - [东北师范大学2025年本科招生章程](http://zsb.nenu.edu.cn/info/1007/4280.htm) `2025-05-29`
  - 来源：东北师范大学本科招生网招生章程栏目页
    - 栏目页：`http://zsb.nenu.edu.cn/bkzn/zszc.htm`
  - 同批缓存中已确认学校侧系统入口：
    - 官方招生系统首页：`https://gkcx.nenu.edu.cn/`
    - 历史分数入口：`https://gkcx.nenu.edu.cn/history_score.html`
  - 价值：
    1. 补齐东北师范大学 `2025` 官方章程基线。
    2. 把章程栏目页与学校侧招生系统、历史分数入口正式绑在一起。
    3. 为后续对比 `2026` 章程变化与继续服务器侧补抓提供稳定入口。

- 新增补齐一条 **贵州大学 2025 官方普通本科招生计划基线**：
  - [贵州大学2025年普通本科招生计划（含国家专项、地方专项）](https://rso.gzu.edu.cn/2025/0620/c17370a252806/page.htm) `2025-06-20`
  - 来源：贵州大学本科招生网招生计划栏目
    - 栏目页：`https://rso.gzu.edu.cn/zsjh_17370/list.htm`
  - 正文直接给出 `2025` 普通本科招生计划总表，表头已明确包含 `桂` 列。
  - 同校已在项目中登记的官方基线：
    - [贵州大学2025年本科招生章程](https://rso.gzu.edu.cn/2025/0513/c17366a250006/page.htm) `2025-05-13`
    - 录取查询栏目：`https://rso.gzu.edu.cn/lqcx/list.htm`
  - 价值：
    1. 把贵州大学从“只有 `2025` 章程基线”推进到“章程 + 计划正文”双基线。
    2. 计划页正文已经包含广西列，后续如果要继续抽取贵州大学广西计划，优先级很高。
    3. 为后续对比 `2026` 学校侧计划入口与内容变化提供明确的 `2025` 官方参照。

- 新增补齐一条 **四川农业大学官方历年分数查询入口基线**：
  - [2023-2025年在各省、自治区、直辖市录取分数线](https://zs.sicau.edu.cn/lnfsxcx.htm) `2024年03月14日`
  - 来源：四川农业大学本科招生网历年分数线查询栏目
  - 列表条目直接指向学校官方查询系统：
    - `https://zsdata.sicau.edu.cn/zsdata/lqxx/#/lnfs`
  - 同批缓存中还存在学校侧 `2025` 招生计划入口页：
    - `https://zs.sicau.edu.cn/zszn1/zsjh.htm`
    - 正文明确写到：`四川农业大学2025年招生计划`，并直接给出计划查询系统 `https://zsdata.sicau.edu.cn/zsdata/lqxx/#/zsjh`
  - 价值：
    1. 正式补出四川农业大学这所 `211` 学校的学校侧官方分数查询入口基线。
    2. 同批缓存已经把川农的计划入口与分数入口同时锚定出来，后续服务器侧继续追广西计划/分数时路径很清晰。
    3. 这条来源对“学校侧可复用查询系统入口”的覆盖有补强价值，即使当前还没在本地缓存里看到单独的广西明细页。

- 新增补齐一条 **西南财经大学 2025 官方招生专业（类）一览表基线**：
  - [西南财经大学2025年普通本科招生专业（类）一览表](https://zb.swufe.edu.cn/info/2581/8361.htm) `2025.05.29`
  - 来源：西南财经大学本科招生网
  - 正文直接给出 `2025` 普通本科招生专业（类）一览表，覆盖：
    - 专业（类）与包含专业
    - 学费标准
    - 高考综合改革省份选考科目要求
    - 文理分科省份科类要求
    - 中外合作办学 / 双学位等备注
  - 同校已在项目中登记的官方基线：
    - [西南财经大学2025年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/8321.htm) `2025-05-29`
    - 官方数据查询入口：`https://zsdata.swufe.edu.cn/zsdata/lqxx.html`
  - 价值：
    1. 把西南财经大学从“只有 `2025` 章程基线”推进到“章程 + 招生专业（类）清单”双基线。
    2. 这条正文把选考科目和专业范围正式落到了学校官方页上，后续比对广西物理类匹配关系会更稳。
    3. 为后续服务器侧继续追分省计划、广西计划和学校侧查询系统变化提供了新的校内锚点。

- 新增补齐两条 **辽宁大学广西学校侧列表项基线**：
  - [广西壮族自治区2025年招生计划](http://zs.lnu.edu.cn/info/14380/71566.htm) `2025-06-26`
    - 来源：辽宁大学本科招生网招生计划列表页
    - 列表页：`http://zs.lnu.edu.cn/cxzx/zsjh.htm`
  - [广西壮族自治区2025年录取情况](http://zs.lnu.edu.cn/info/14381/71619.htm) `2026-01-13`
    - 来源：辽宁大学本科招生网历年录取情况列表页
    - 列表页：`http://zs.lnu.edu.cn/cxzx/lnlqqk1.htm`
  - 价值：
    1. 把此前只写在辽宁大学章程备注里的广西计划 / 录取结果线索，正式拆成可检索的独立官方来源。
    2. 后续如果要服务器侧继续补辽宁大学广西计划明细和录取结果明细，这两条就是最直接的校内入口。
    3. 对“目标校学校侧广西专页是否已公开、何时公开”的跟踪更完整了。

- 新增补齐一条 **中国药科大学广西学校侧招生计划列表项基线**：
  - [2025年广西招生计划](http://zb.cpu.edu.cn/2d/1d/c12765a208157/page.htm) `2025-06-23`
    - 来源：中国药科大学本科招生网 `2025招生计划` 列表页
    - 列表页：`http://zb.cpu.edu.cn/gszszn/list.htm`
  - 同页还能看到多省分招生计划条目，说明 `2025招生计划` 是学校侧按省份拆分发布的正式栏目，而不是单一总表或外链跳转页。
  - 同校已在项目中登记的官方基线：
    - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
  - 价值：
    1. 把中国药科大学从“只有 `2025` 章程基线”推进到“章程 + 广西学校侧计划入口”双基线。
    2. 列表页直接出现 `2025年广西招生计划` 子页链接，后续服务器侧补抓广西专业计划明细时路径非常明确。
    3. 对“学校是否公开分省单页计划”这类跟踪维度也补出了一条新的正式案例。

- 新增补齐一条 **华南师范大学 2025 外省招生计划正文页基线**：
  - [2025年华南师范大学外省招生计划和招生情况表](http://zsb.scnu.edu.cn/a/20250619/693.html) `2025-06-19 12:32:00`
    - 来源：华南师范大学本科招生网
  - 正文不是简单列表壳页，而是直接挂出：
    - 外省招生计划总表 `.xlsx`
    - 多个分省 PDF
    - 其中明确包含 `7、2025年华南师范大学外省招生计划（广西）.pdf`
  - 广西 PDF 直链：
    - `https://statics.scnu.edu.cn/pics/zsb/2025/0701/1751333491762237.pdf`
  - 同校已在项目中登记的官方基线：
    - [华南师范大学2025年夏季高考招生章程](http://zsb.scnu.edu.cn/a/20250515/684.html) `2025-05-15 10:15:00`
  - 价值：
    1. 把华南师范大学从“只有 `2025` 章程基线”推进到“章程 + 外省分省计划正文”双基线。
    2. 这条正文页已经把广西分省 PDF 明确暴露出来，后续服务器侧补抓华师广西计划明细路径非常直接。
    3. 对“学校侧是否公开分省计划附件、是否公开广西子文件”这一跟踪维度有明显补强。

- 新增补齐一条 **北京工业大学 2025 官方招生计划栏目页基线**：
  - [招生计划-北工大本科招生网](http://admissions.bjut.edu.cn/zsxx/zsjh.htm)
    - 列表中的 `2025` 条目为：
      - `北京工业大学2025年分省分专业招生计划` `2025-06-19 10:00`
      - 附件直链：`https://admissions.bjut.edu.cn/dfiles/2025/2025gaigeshengfenjh.pdf`
  - 同校已在项目中登记的官方基线：
    - [北京工业大学2025年京外本科普通批分省分专业招生计划 PDF](https://admissions.bjut.edu.cn/dfiles/2025/2025gaigeshengfenjh.pdf)
    - [2025年北京工业大学京外省份普通类录取分数统计](https://admissions.bjut.edu.cn/lnlqfs/1776.htm)
  - 价值：
    1. 把北工大的 `2025` 计划源从“只有附件级 PDF”推进到“学校侧正式栏目页 + PDF”双锚点。
    2. 栏目页给出了明确发布时间，后续比对学校计划发布时间线更稳。
    3. 如果后面要继续补北工大广西相关明细，这个栏目页比孤立附件更适合作为稳定入口。

- 新增补齐一条 **南京航空航天大学 2024 官方招生章程基线**：
  - [南京航空航天大学2024年本科招生章程](https://zs.nuaa.edu.cn/2024/0529/c9155a345273/page.htm) `2024-05-29`
    - 来源：南京航空航天大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [南京航空航天大学2025年本科招生章程](https://zs.nuaa.edu.cn/2025/0530/c9155a376532/page.htm) `2025-05-30`
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 把南航从“只有 `2025` 章程基线”推进到“`2024` + `2025` 连续章程基线”。
    2. 这对后续追踪 `2026` 招生章程入口变化、条文变化和学校侧系统变化更有帮助。
    3. 对工程类目标校的连续年度基线覆盖也更完整。

- 新增补齐一条 **南京航空航天大学 2023 官方招生章程基线**：
  - [南京航空航天大学2023年本科招生章程](https://zs.nuaa.edu.cn/2023/0605/c9155a312135/page.htm) `2023-06-05`
    - 来源：南京航空航天大学本科招生网
  - 正文明确写到：
    - 招生网址为 `http://zs.nuaa.edu.cn`
  - 同校已在项目中登记的官方基线：
    - [南京航空航天大学2024年本科招生章程](https://zs.nuaa.edu.cn/2024/0529/c9155a345273/page.htm) `2024-05-29`
    - [南京航空航天大学2025年本科招生章程](https://zs.nuaa.edu.cn/2025/0530/c9155a376532/page.htm) `2025-05-30`
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 把南航这条学校侧章程基线再向前延伸到 `2023`。
    2. 让南航形成 `2023 + 2024 + 2025` 的连续官方章程序列，方便后续比较 `2026` 入口与条文变化。
    3. 这条证据完全来自本地已缓存官方正文页，不需要再重复高成本探测。

- 新增补齐一条 **南京航空航天大学 2022 官方招生章程基线**：
  - [南京航空航天大学2022年本科招生章程](https://zs.nuaa.edu.cn/2022/0501/c9155a283210/page.htm) `2022-05-01`
    - 来源：南京航空航天大学本科招生网
  - 正文明确写到：
    - 招生网址为 `http://zs.nuaa.edu.cn`
  - 同校已在项目中登记的官方基线：
    - [南京航空航天大学2023年本科招生章程](https://zs.nuaa.edu.cn/2023/0605/c9155a312135/page.htm) `2023-06-05`
    - [南京航空航天大学2024年本科招生章程](https://zs.nuaa.edu.cn/2024/0529/c9155a345273/page.htm) `2024-05-29`
    - [南京航空航天大学2025年本科招生章程](https://zs.nuaa.edu.cn/2025/0530/c9155a376532/page.htm) `2025-05-30`
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 把南航学校侧章程序列再向前延伸到 `2022`。
    2. 让南航形成 `2022 + 2023 + 2024 + 2025` 的连续官方章程时间线，方便后续比较 `2026` 入口和条文变化。
    3. 这条证据同样完全来自本地已缓存官方正文页，不需要再重复高成本探测。

- 新增补齐一条 **河北工业大学 2025 官方招生计划正文页基线**：
  - [河北工业大学2025年本科招生计划](https://zs.hebut.edu.cn/2025-06-16/214.html) `2025-06-16`
    - 来源：河北工业大学招生办公室
  - 正文不是列表壳页，而是直接挂出计划附件：
    - `河北工业大学2025年本科招生计划（网站公布版）.pdf`
    - 附件直链：`https://zs.hebut.edu.cn/Upload/file/20250630/1751266683401513.pdf`
  - 同校已在项目中登记的官方基线：
    - [河北工业大学 2025 广西招生计划 PDF](https://zs.hebut.edu.cn/Upload/file/20250630/1751266683401513.pdf)
    - [河北工业大学广西本科普通批录取完成通知](https://zs.hebut.edu.cn/2025-07-12/216.html)
  - 价值：
    1. 把河北工大的 `2025` 计划来源从“只有附件级 PDF”推进到“学校侧正式正文页 + PDF + 广西结果通知”三点锚定。
    2. 正文页给出了明确发布日期，有助于后续跟踪学校计划发布时间线。
    3. 后续如果继续服务器侧追广西计划细项，这条正文页会比单独附件更稳。

- 新增补齐一条 **贵州大学 2024 官方招生计划基线**：
  - [贵州大学2024年普通类专业招生计划](https://rso.gzu.edu.cn/2024/0621/c17370a220346/page.htm) `2024-06-21`
    - 来源：贵州大学招生办公室
  - 正文为学校侧完整计划表，而不是外链附件；表头按省份展开，其中包含 `桂` 列。
  - 同校已在项目中登记的官方基线：
    - [贵州大学2025年本科招生章程](https://rso.gzu.edu.cn/2025/0513/c17366a250006/page.htm) `2025-05-13`
    - [贵州大学2025年普通本科招生计划（含国家专项、地方专项）](https://rso.gzu.edu.cn/2025/0620/c17370a252806/page.htm) `2025-06-20`
  - 价值：
    1. 把贵州大学从“只有 `2025` 计划页”推进到“`2024` + `2025` 连续计划基线”。
    2. 这对后续比较学校侧广西计划是否变化、哪些专业在 `2025` 新增或缩减更有帮助。
    3. 也补强了“学校侧正文表格直接含省份列”这一类高价值计划源案例。

- 新增补齐一组 **东北林业大学 2022-2024 官方招生章程基线**：
  - [东北林业大学2024年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/4303.htm) `2024-05-24`
  - [东北林业大学2023年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/4117.htm) `2023-06-05`
  - [东北林业大学2022年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/3615.htm) `2022-05-20`
    - 来源：东北林业大学本科招生信息网
  - 同校已在项目中登记的官方基线：
    - [东北林业大学2025年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/4501.htm) `2025-05-29`
    - [东北林业大学2025年招生计划](http://zhaosheng.nefu.edu.cn/info/1008/4534.htm) `2025-06-25`
  - 价值：
    1. 让东北林业大学形成 `2022 + 2023 + 2024 + 2025` 的连续官方章程时间线。
    2. 后续如果继续追学校侧招生计划和录取查询入口变化，这组基线能更稳地做 `2026` 对比。

- 新增补齐一组 **郑州大学 2022-2024 官方招生章程基线**：
  - [郑州大学2024年本科招生章程](http://ao.zzu.edu.cn/info/1793/4623.htm) `2024-05-23`
  - [郑州大学2023年本科招生章程](http://ao.zzu.edu.cn/info/1793/4255.htm) `2023-05-22`
  - [郑州大学2022年本科招生章程](http://ao.zzu.edu.cn/info/1793/3934.htm) `2022-05-06`
    - 来源：郑州大学招生网
  - 同页导航同时锚定：
    - 招生计划：`http://ao.zzu.edu.cn/xxgk/zsjh_/gx/a2025.htm`
    - 历年录取：`http://ao.zzu.edu.cn/xxgk/lnlq/gx/a2025.htm`
  - 价值：
    1. 把郑州大学从“只有 `2025` 章程 + 广西计划/分数结果页”推进到连续的学校侧章程时间线。
    2. 这有助于后续比较学校章程条文变化和广西来源发布时间线。

- 新增补齐一组 **东北师范大学 2022-2024 官方招生章程基线**：
  - [东北师范大学2024年本科招生章程](http://zsb.nenu.edu.cn/info/1007/3928.htm) `2024-06-02`
  - [东北师范大学2023年本科招生章程](http://zsb.nenu.edu.cn/info/1007/3473.htm) `2023-06-05`
  - [东北师范大学2022年本科招生章程](http://zsb.nenu.edu.cn/info/1007/3086.htm) `2022-05-23`
    - 来源：东北师范大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [东北师范大学2025年本科招生章程](http://zsb.nenu.edu.cn/info/1007/4280.htm) `2025-05-29`
  - 同批缓存里还存在学校侧入口：
    - 招生系统首页：`https://gkcx.nenu.edu.cn/`
    - 历史分数入口：`https://gkcx.nenu.edu.cn/history_score.html`
  - 价值：
    1. 让东北师范大学形成 `2022 + 2023 + 2024 + 2025` 的连续官方章程时间线。
    2. 后续如果继续补学校侧查询入口或广西结果，这组基线能更稳地支撑 `2026` 变化对比。

- 新增补齐一组 **中国传媒大学 2023-2024 官方招生章程基线**：
  - [中国传媒大学2024年本科招生章程](https://zhaosheng.cuc.edu.cn/2024/0520/c5852a219907/page.htm) `2024-05-24`
  - [中国传媒大学2023年本科招生章程](https://zhaosheng.cuc.edu.cn/2023/0531/c5852a209329/page.htm) `2023-05-31`
    - 来源：中国传媒大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [中国传媒大学2025年本科招生章程](https://zhaosheng.cuc.edu.cn/2025/0530/c5852a256319/page.htm) `2025-05-30`
  - 价值：
    1. 让中国传媒大学形成 `2023 + 2024 + 2025` 的连续官方章程时间线。
    2. 后续如果继续比较学校侧章程条文或入口变化，这组基线会更稳。

- 新增补齐一组 **华东理工大学 2023-2024 官方招生章程基线**：
  - [华东理工大学2024年本科招生章程](https://zsb.ecust.edu.cn/2024/0524/c2309a167836/page.htm) `2024-05-24`
  - [华东理工大学2023年本科招生章程](https://zsb.ecust.edu.cn/2023/0604/c2309a156688/page.htm) `2023-06-04`
    - 来源：华东理工大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [华东理工大学2025年本科招生章程](https://zsb.ecust.edu.cn/2025/0529/c2307a179246/page.htm) `2025-05-29`
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 让华东理工大学形成 `2023 + 2024 + 2025` 的连续官方章程时间线。
    2. 这也让已登记的学校侧计划 / 分数 API 有了更完整的章程对照背景，便于后续比较 `2026` 入口和说明文字变化。

- 新增补齐一组 **武汉理工大学 2021-2024 官方招生章程基线**：
  - [武汉理工大学2024年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004339.shtml) `2024-05-27`
  - [武汉理工大学2023年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004355.shtml) `2023-05-29`
  - [武汉理工大学2022年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004356.shtml) `2022-05-27`
  - [武汉理工大学2021年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004354.shtml) `2021-06-07`
    - 来源：武汉理工大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [武汉理工大学2025年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202505/t20250530_1331279.shtml) `2025-05-30`
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 让武汉理工大学形成 `2021 + 2022 + 2023 + 2024 + 2025` 的连续官方章程时间线。
    2. 这也让已登记的学校侧计划 / 分数 API 有了完整得多的章程背景，便于后续比较 `2026` 入口和说明变化。

- 新增补齐一组 **太原理工大学 2020-2023 官方招生章程基线**：
  - [太原理工大学2023年本科招生章程](http://zs.tyut.edu.cn/info/1006/2107.htm) `2023-05-16`
  - [太原理工大学2021年本科招生章程](http://zs.tyut.edu.cn/info/1006/1696.htm) `2021-05-14`
  - [太原理工大学2020年本科招生章程](http://zs.tyut.edu.cn/info/1006/1553.htm) `2020-07-02`
    - 来源：太原理工大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [太原理工大学2024年本科招生章程](http://zs.tyut.edu.cn/info/1006/2927.htm) `2024-05-21`
    - [太原理工大学2025年本科招生章程](http://zs.tyut.edu.cn/info/1006/4687.htm) `2025-05-15`
  - 价值：
    1. 让太原理工大学从“只到 2024/2025”推进到覆盖 `2020 + 2021 + 2023 + 2024 + 2025` 的更长时间线。
    2. 后续如果继续比较学校侧章程与计划入口变化，这组更长的基线会更有参考价值。

- 新增补齐一组 **武汉理工大学 2018-2020 官方招生章程基线**：
  - [武汉理工大学2020年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004349.shtml) `2020-07-02`
  - [武汉理工大学2019年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004350.shtml) `2019-06-06`
  - [武汉理工大学2018年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004351.shtml) `2018-06-12`
    - 来源：武汉理工大学本科招生网
  - 同校已在项目中登记的官方基线：
    - `2021-2025` 连续章程基线
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 让武汉理工大学章程时间线进一步向前延伸到 `2018`。
    2. 这让后续比较学校侧入口、字段说明和规则文字变化时，有了更完整的长期参照。

- 新增补齐一组 **东北师范大学 2019-2021 官方招生章程基线**：
  - [东北师范大学2021年本科招生章程](http://zsb.nenu.edu.cn/info/1007/2629.htm) `2021-06-06`
  - [东北师范大学2020年本科招生章程](http://zsb.nenu.edu.cn/info/1007/2143.htm) `2020-07-02`
  - [东北师范大学2019年本科招生章程](http://zsb.nenu.edu.cn/info/1007/1279.htm) `2019-06-06`
    - 来源：东北师范大学本科招生网
  - 同校已在项目中登记的官方基线：
    - `2022-2025` 连续章程基线
    - 学校侧招生系统首页与历史分数入口
  - 价值：
    1. 让东北师范大学形成 `2019-2025` 的连续学校侧章程时间线。
    2. 后续如果继续补查询入口或比对章程条文变化，这组更长时间线会更稳。

- 新增补齐一组 **中国传媒大学 2021-2022 官方招生章程基线**：
  - [中国传媒大学2022年招生章程](https://zhaosheng.cuc.edu.cn/2022/0519/c5852a193800/page.htm) `2022-05-19`
  - [中国传媒大学2021年招生章程](https://zhaosheng.cuc.edu.cn/2021/0607/c5852a182536/page.htm) `2021-06-07`
    - 来源：中国传媒大学本科招生网
  - 同校已在项目中登记的官方基线：
    - `2023-2025` 连续章程基线
  - 价值：
    1. 让中国传媒大学形成 `2021-2025` 的连续学校侧章程时间线。
    2. 这能为后续比较章程命名、入口和条文变化提供更早的对照背景。

- 新增补齐一组 **武汉理工大学 2016-2017 官方招生章程基线**：
  - [武汉理工大学2017年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004352.shtml) `2017-06-05`
  - [武汉理工大学2016年普通本科招生章程](https://zs.whut.edu.cn/zc/zszc/202406/t20240621_1004353.shtml) `2016-06-01`
    - 来源：武汉理工大学本科招生网
  - 同校已在项目中登记的官方基线：
    - `2018-2025` 连续章程基线
    - 学校侧官方计划 / 分数 API
  - 价值：
    1. 让武汉理工大学学校侧章程时间线进一步前推到 `2016`。
    2. 这对后续比较学校侧规则文本与入口稳定性变化更有帮助。

- 新增补齐一组 **东北师范大学 2017-2018 官方招生章程基线**：
  - [东北师范大学2018年本科招生章程](http://zsb.nenu.edu.cn/info/1007/1193.htm) `2018-06-10`
  - [东北师范大学2017年本科招生章程](http://zsb.nenu.edu.cn/info/1007/1194.htm) `2017-06-08`
    - 来源：东北师范大学本科招生网
  - 同校已在项目中登记的官方基线：
    - `2019-2025` 连续章程基线
    - 学校侧招生系统首页与历史分数入口
  - 价值：
    1. 让东北师范大学学校侧章程时间线进一步前推到 `2017`。
    2. 后续如果继续比对学校侧章程和查询入口演变，这组更长时间线会更稳。

- 新增补齐一组 **海南大学 2021-2024 官方招生章程基线**：
  - [海南大学2024年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/4047.htm) `2024-05-21`
  - [海南大学2023年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/2666.htm) `2023-05-10`
  - [海南大学2022年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1003/2332.htm) `2022-05-09`
  - [海南大学2021年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1003/2004.htm) `2021-05-27`
    - 来源：海南大学招生信息网
  - 同校已在项目中登记的官方基线：
    - [海南大学2025年本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/5087.htm) `2025-05-28`
    - 学校侧招生计划 / 历年分数 / 录取进程 / 录取查询入口
  - 价值：
    1. 让海南大学形成 `2021-2025` 的连续学校侧章程时间线。
    2. 这条线还同时锚定了学校侧计划和分数查询入口，后续补学校侧变化时会更稳。

- 新增补齐一组 **海南大学 2016-2020 官方招生章程基线**：
  - [海南大学2020年本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1846.htm) `2020-06-28`
  - [海南大学2019年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1261.htm) `2019-06-03`
  - [海南大学2018年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1130.htm) `2018-06-01`
  - [海南大学2017年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1241.htm) `2017-05-22`
  - [海南大学2016年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1228.htm) `2016-05-13`
    - 来源：海南大学招生信息网
  - 同校已在项目中登记的官方基线：
    - `2021-2025` 连续章程基线
    - 学校侧招生计划 / 历年分数 / 录取进程 / 录取查询入口
  - 价值：
    1. 让海南大学学校侧章程时间线进一步前推到 `2016`。
    2. 这条线同时锚定学校侧计划和分数查询入口，后续比较入口与规则演变时会更稳。

- 新增补齐两条 **辽宁大学 2024 广西直达列表项**：
  - [广西壮族自治区2024年招生计划](http://zs.lnu.edu.cn/info/14380/71464.htm) `2024-06-21`
  - [广西壮族自治区2024年录取情况](http://zs.lnu.edu.cn/info/14381/71510.htm) `2025-01-08`
    - 来源：辽宁大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [辽宁大学2025年本科招生章程](http://zs.lnu.edu.cn/info/14170/71533.htm) `2025-05-16 16:58`
    - [广西壮族自治区2025年招生计划](http://zs.lnu.edu.cn/info/14380/71566.htm) `2025-06-26`
    - [广西壮族自治区2025年录取情况](http://zs.lnu.edu.cn/info/14381/71619.htm) `2026-01-13`
  - 价值：
    1. 把辽宁大学这条广西直达链从“只有 `2025`”推进到“`2024 + 2025` 连续对照”。
    2. 对后续追辽宁大学广西计划和录取结果变化会更直接有用。

- 新增补齐一组 **东华大学学校侧计划时间线锚点**：
  - [东华大学2025年各类型分省分专业招生计划](http://zs.dhu.edu.cn/2025/0619/c22353a363015/page.htm) `2025-06-19`
  - [东华大学2023年普通类本科一批非高考改革省份各专业招生计划](http://zs.dhu.edu.cn/2023/0615/c22353a326939/page.htm) `2023-06-15`
  - [2022年东华大学普通类分省分专业招生计划安排表](http://zs.dhu.edu.cn/2022/0620/c22353a296676/page.htm) `2022-06-20`
    - 来源：东华大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [东华大学2025年本科招生章程](http://zs.dhu.edu.cn/2025/0522/c9563a361995/page.htm) `2025-05-22`
    - [东华大学2025年各省市录取分数查询（广西物化组）](http://zs.dhu.edu.cn/2026/0227/c25199a371750/page.htm)
  - 价值：
    1. 把东华大学从“只有章程 + 广西录取分数文章”推进到“章程 + 学校侧计划发布页 + 录取分数文章”的更完整链路。
    2. 这也让东华大学学校侧计划时间线至少覆盖到 `2022 + 2023 + 2025`，便于后续比较分省分专业计划发布方式变化。

- 新增补齐一组 **江南大学 2020-2024 官方招生章程基线**：
  - [江南大学2024年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2651.htm) `2024-05-27`
  - [江南大学2023年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2593.htm) `2023-06-05`
  - [江南大学2022年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2461.htm) `2022-05-20`
  - [江南大学2021年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2353.htm) `2021-06-09`
  - [江南大学2020年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2183.htm) `2020-07-03`
    - 来源：江南大学本科招生网
  - 同校已在项目中登记的官方基线：
    - [江南大学2025年本科生招生章程](http://admission.jiangnan.edu.cn/info/1004/2713.htm) `2025-05-30`
  - 价值：
    1. 让江南大学从“只有 `2025` 单点章程基线”推进到 `2020-2025` 连续学校侧章程时间线。
    2. 这会显著增强后续比较江南大学 `2026` 招生章程入口与条文变化的可操作性。

- 新增补齐一组 **太原理工大学 2016-2019 及 2022 官方招生章程基线**：
  - [太原理工大学2022年本科招生章程](https://mp.weixin.qq.com/s/PD1wqoJvg7tmy27Z_CSU_A) `2022-05-11`
  - [太原理工大学2019年本科招生章程](http://zs.tyut.edu.cn/info/1006/1367.htm) `2019-05-24`
  - [太原理工大学2018年本科招生章程](http://zs.tyut.edu.cn/info/1006/1226.htm) `2018-06-13`
  - [太原理工大学2016年本科招生章程](http://zs.tyut.edu.cn/info/1006/1064.htm) `2016-06-07`
    - 来源：太原理工大学本科招生网
  - 补充说明：
    - `2022` 条目在学校官网招生章程列表页中明确给出标题与日期，但实际跳转为官方微信文章。
  - 同校已在项目中登记的官方基线：
    - `2020 + 2021 + 2023 + 2024 + 2025` 连续章程基线
  - 价值：
    1. 让太原理工大学学校侧章程时间线进一步延展为覆盖 `2016-2025` 的长序列。
    2. 这对后续比较学校侧章程、入口与规则表述变化会更有参考价值。

- 新增补齐一组 **江南大学 2015-2019 官方招生章程基线**：
  - [江南大学2019年本科生招生章程](http://admission.jiangnan.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1004&wbnewsid=1909) `2019-06-07`
  - [江南大学2018年本科生招生章程](http://admission.jiangnan.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1004&wbnewsid=1709) `2018-06-09`
  - [江南大学2017年本科生招生章程](http://admission.jiangnan.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1004&wbnewsid=1529) `2017-06-07`
  - [江南大学2016年本科生招生章程](http://admission.jiangnan.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1004&wbnewsid=1528) `2016-05-09`
  - [江南大学2015年本科生招生章程](http://admission.jiangnan.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1004&wbnewsid=1527) `2015-06-08`
    - 来源：江南大学本科招生网
  - 同校已在项目中登记的官方基线：
    - `2020-2025` 连续章程基线
  - 价值：
    1. 让江南大学学校侧章程时间线进一步前推到 `2015`，形成 `2015-2025` 连续长序列。
    2. 这会进一步增强后续比较江南大学 `2026` 招生章程入口与条文变化的可操作性。

- 新增补齐一组 **海南大学 2006-2015 官方招生章程基线**：
  - [海南大学2015年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1218.htm) `2015-05-18`
  - [海南大学2014年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1211.htm) `2014-04-21`
  - [海南大学2013年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1202.htm) `2013-04-12`
  - [海南大学2012年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1193.htm) `2012-04-26`
  - [海南大学2011年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1190.htm) `2011-04-19`
  - [海南大学2010年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1187.htm) `2010-04-12`
  - [海南大学2009年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1184.htm) `2009-04-27`
  - [海南大学2008年全日制本科招生章程](https://bkzs.hainanu.edu.cn/info/1005/1180.htm) `2008-04-02`
  - [海南大学2007年招生章程](https://bkzs.hainanu.edu.cn/info/1005/1178.htm) `2007-04-17`
  - [海南大学2006年招生章程](https://bkzs.hainanu.edu.cn/info/1005/1175.htm) `2006-04-20`
    - 来源：海南大学招生信息网
    - 对照锚点：
      - [海南大学招生章程栏目页](https://bkzs.hainanu.edu.cn/zsxx/zszc.htm)
      - 招生计划：`https://zsfw.hainanu.edu.cn/static/front/hainanu/basic/html_web/zsjh.html`
      - 历年分数：`https://zsfw.hainanu.edu.cn/static/front/hainanu/basic/html_web/lnfs.html`
  - 同校已在项目中登记的官方基线：
    - `2016-2025` 连续章程基线
  - 价值：
    1. 让海南大学学校侧招生章程时间线进一步前推到 `2006`，形成 `2006-2025` 连续长序列。
    2. 这会显著增强后续比较海南大学 `2026` 招生章程入口、挂载系统入口与条文变化的可操作性。

- 新增补齐一组 **东北林业大学 2016-2021 官方招生章程基线**：
  - [东北林业大学2021年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/3257.htm) `2021-06-04`
  - [东北林业大学2020年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/2912.htm) `2020-07-01`
  - [东北林业大学2019年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/2202.htm) `2019-06-16`
  - [东北林业大学2018年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/2061.htm) `2018-06-10`
  - [东北林业大学2017年本科招生章程](http://zhaosheng.nefu.edu.cn/info/1003/2062.htm) `2017-06-06`
  - [东北林业大学本科招生工作章程（2016年）](http://zhaosheng.nefu.edu.cn/info/1003/2063.htm) `2016-05-10`
    - 来源：东北林业大学本科招生信息网
    - 对照锚点：
      - [东北林业大学招生章程栏目页](http://zhaosheng.nefu.edu.cn/zszc.htm)
      - [东北林业大学2025年招生计划](http://zhaosheng.nefu.edu.cn/info/1008/4534.htm) `2025-06-25`
  - 同校已在项目中登记的官方基线：
    - `2022-2025` 连续章程基线
  - 价值：
    1. 让东北林业大学学校侧招生章程时间线补齐为 `2016-2025` 连续序列。
    2. 这会增强后续比较学校侧 `2026` 章程入口与条文变化的可操作性。

- 新增补齐一组 **郑州大学 2020-2021 官方招生章程基线**：
  - [郑州大学2021年本科招生章程](http://ao.zzu.edu.cn/info/1793/3493.htm) `2021-05-25`
  - [郑州大学2020年本科招生章程](http://ao.zzu.edu.cn/info/1793/3096.htm) `2020-07-17`
    - 来源：郑州大学招生网
    - 对照锚点：
      - [郑州大学招生章程栏目页](http://ao.zzu.edu.cn/xxgk/zszc.htm)
      - [郑州大学2025年广西招生计划 PDF](https://ao.zzu.edu.cn/__local/B/26/EB/BA1AA1F04FE2D060489EB73C48F_613A53AF_E94F.pdf)
      - [郑州大学广西历年录取页（2024-2025）](https://ao.zzu.edu.cn/xxgk/lnlq/gx/a2025.htm)
  - 同校已在项目中登记的官方基线：
    - `2022-2025` 连续章程基线
    - 广西 `2024-2025` 计划与专业分来源
  - 价值：
    1. 让郑州大学学校侧招生章程时间线补齐为 `2020-2025` 连续序列。
    2. 这会增强后续比较学校侧 `2026` 章程入口与条文变化的可操作性，也让广西计划/分数链路有更长的规则对照基线。

- 新增补齐一组 **中国药科大学 2022-2023 官方招生章程基线**：
  - [中国药科大学2023年普通本科招生章程](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=193167) `2023-10-30`
  - [中国药科大学2022年普通本科招生章程](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=176448) `2022-11-09`
    - 来源：中国药科大学本科生招生网
    - 对照锚点：
      - [中国药科大学招生政策列表页](http://zjc.cpu.edu.cn/zszcjtslxzsbf/list.htm)
      - [中国药科大学2024年普通本科招生章程](http://zb.cpu.edu.cn/2b/1f/c9133a207647/page.htm) `2024-06-12`
      - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
      - [中国药科大学2025年广西招生计划](http://zb.cpu.edu.cn/2d/1d/c12765a208157/page.htm) `2025-06-23`
  - 价值：
    1. 让中国药科大学学校侧招生章程时间线从 `2024-2025` 延展到 `2022-2025`。
    2. 这会增强后续比较学校侧 `2026` 章程入口与条文变化的可操作性，并补厚已登记广西计划来源前后的规则对照链。

- 新增补齐一组 **东华大学 2022-2025 学校侧专项与分类型招生计划基线**：
  - [东华大学2025年国家专项各省招生计划](http://zs.dhu.edu.cn/2025/0616/c22353a362933/page.htm) `2025-06-16`
  - [东华大学2025年高校专项各省招生计划](http://zs.dhu.edu.cn/2025/0616/c22353a362932/page.htm) `2025-06-16`
  - [东华大学2024年国家专项各省招生计划](http://zs.dhu.edu.cn/2024/0626/c22353a347719/page.htm) `2024-06-26`
  - [东华大学2024年高校专项各省招生计划](http://zs.dhu.edu.cn/2024/0626/c22353a347718/page.htm) `2024-06-26`
  - [东华大学2023年普通类本科一批3+1+2高考改革省份各专业招生计划](http://zs.dhu.edu.cn/2023/0615/c22353a326938/page.htm) `2023-06-15`
  - [东华大学2023年普通类本科一批3+3高考改革省份各专业招生计划](http://zs.dhu.edu.cn/2023/0615/c22353a326937/page.htm) `2023-06-15`
  - [东华大学2023年国家专项各省招生计划](http://zs.dhu.edu.cn/2023/0615/c22353a326877/page.htm) `2023-06-15`
  - [东华大学2023年高校专项各省招生计划](http://zs.dhu.edu.cn/2023/0615/c22353a326864/page.htm) `2023-06-15`
  - [2022年东华大学国家专项计划分省分专业计划安排](http://zs.dhu.edu.cn/2022/0620/c22353a296674/page.htm) `2022-06-20`
  - [2022年东华大学高校专项计划分省分专业计划安排](http://zs.dhu.edu.cn/2022/0620/c22353a296673/page.htm) `2022-06-20`
    - 来源：东华大学本科招生网招生计划栏目
    - 对照锚点：
      - [东华大学招生计划栏目页](http://zs.dhu.edu.cn/zsjh/list.htm)
      - [东华大学2025年本科招生章程](http://zs.dhu.edu.cn/2025/0522/c9563a361995/page.htm) `2025-05-22`
      - [东华大学2025年各类型分省分专业招生计划](http://zs.dhu.edu.cn/2025/0619/c22353a363015/page.htm) `2025-06-19`
  - 价值：
    1. 把东华大学从“普通计划锚点 + 广西录取分数文章”推进到“普通计划 + 国家专项 + 高校专项 + 高考改革分类型计划”的更完整学校侧计划链路。
    2. 这让东华大学学校侧计划时间线在 `2022-2025` 之间的发布方式变化更容易做横向对比，也为后续筛广西相关细分入口提供更多稳定锚点。

- 新增补齐一组 **西南财经大学 2021-2024 官方招生章程基线**：
  - [西南财经大学2024年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/7301.htm) `2024-05-24`
  - [西南财经大学2023年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/6341.htm) `2023-05-31`
  - [西南财经大学2022年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/6351.htm) `2022-05-30`
  - [西南财经大学2021年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/6361.htm) `2021-06-04`
    - 来源：西南财经大学本科招生网
    - 对照锚点：
      - [西南财经大学招生章程栏目页](https://zb.swufe.edu.cn/zszc1.htm)
      - [西南财经大学2025年普通本科招生章程](https://zb.swufe.edu.cn/info/2801/8321.htm) `2025-05-29`
      - 官方数据查询入口：`https://zsdata.swufe.edu.cn/zsdata/lqxx.html`
  - 价值：
    1. 让西南财经大学学校侧招生章程时间线从“只有 `2025` 单点基线”扩展为 `2021-2025` 连续序列。
    2. 这会增强后续比较学校侧 `2026` 章程入口与条文变化的可操作性，也让已登记的专业一览表与数据查询入口有更长的规则对照基线。

- 新增补齐一条 **北京科技大学 2024 官方招生章程基线**：
  - [北京科技大学2024年本科招生章程](https://zhaosheng.ustb.edu.cn/zkxx/zszc/bd2e0139b0654c669641e37707826540.htm) `2024-05-24`
    - 来源：北京科技大学本科招生网
    - 对照锚点：
      - [北京科技大学招生章程栏目页](https://zhaosheng.ustb.edu.cn/zkxx/zszc/index.htm)
      - [北京科技大学2025年本科招生章程](https://zhaosheng.ustb.edu.cn/zkxx/zszc/fc4aa12fb8254e97b9ee7a405f57cb8b.htm) `2025-06-04`
      - 招生计划：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/zsjh.html`
      - 历年分数：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/lnfs.html`
  - 价值：
    1. 让北京科技大学从“只有 `2025` 单点章程基线”推进到 `2024-2025` 连续学校侧章程时间线。
    2. 这会增强后续比较学校侧 `2026` 章程入口与条文变化的可操作性，也让此前已确认但受阻的查询系统入口有更稳的上年对照锚点。

- 新增补齐一组 **华南师范大学 学校侧招生计划扩展锚点**：
  - [2025年华南师范大学广东省招生计划和招生情况表](http://zsb.scnu.edu.cn/a/20250619/692.html) `2025-06-19 12:29:00`
    - 附件：`0、2025年华南师范大学广东省招生计划表(总表）.xlsx`
  - [2025年华南师范大学港澳台侨联招招生计划](http://zsb.scnu.edu.cn/a/20250623/714.html) `2025-06-23`
  - [2024年华南师范大学招收港澳台招生计划及往年参考分数](http://zsb.scnu.edu.cn/a/20240630/660.html) `2024-06-30`
    - 来源：华南师范大学本科招生网招生计划栏目
    - 对照锚点：
      - [华南师范大学招生计划栏目页](http://zsb.scnu.edu.cn/zhaoshengjihua/)
      - [2025年华南师范大学外省招生计划和招生情况表](http://zsb.scnu.edu.cn/a/20250619/693.html) `2025-06-19 12:32:00`
      - [华南师范大学2025年夏季高考招生章程](http://zsb.scnu.edu.cn/a/20250515/684.html) `2025-05-15 10:15:00`
  - 价值：
    1. 把华南师范大学从“章程 + 外省计划正文”推进到“广东计划 + 外省计划 + 港澳台侨联招计划”的更完整学校侧计划链路。
    2. 这会让后续比较学校侧计划发布结构、特殊类型入口与分省附件组织方式更容易，也为继续补抓广西相关计划附件提供更完整的上下文锚点。

- 新增补齐一组 **北京工业大学 2022-2024 学校侧招生计划时间线基线**：
  - `2024`：
    - [北京工业大学2024年国家专项分省分专业招生计划](http://admissions.bjut.edu.cn/2024-guojiazhuanxiangjh.pdf) `2024-06-17 14:26`
    - [北京工业大学2024年非高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/2024-feigaigeshengfenjh.pdf) `2024-06-17 14:25`
    - [北京工业大学2024年高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/2024-gaigeshengfenjh.pdf) `2024-06-17 14:12`
  - `2023`：
    - [北京工业大学2023年国家专项分省分专业招生计划](http://admissions.bjut.edu.cn/2023fsfzy_gjzx.pdf) `2023-06-02 07:46`
    - [北京工业大学2023年非高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/2023fsfzy_fgg.pdf) `2023-06-02 07:45`
    - [北京工业大学2023年“3+1+2”高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/2023fsfzy_312.pdf) `2023-06-02 07:43`
    - [北京工业大学2023年“3+3”高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/2023fsfzy_33.pdf) `2023-06-02 07:33`
  - `2022`：
    - [北京工业大学2022年国家专项分省分专业招生计划](http://admissions.bjut.edu.cn/WTYWLLR3SGGUO.pdf) `2022-05-24 19:45`
    - [北京工业大学2022年非高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/AKRGJAKJFGAIRJGPFEI.pdf) `2022-05-24 19:45`
    - [北京工业大学2022年“3+1+2”高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/RTQJRHTQOP4TNA31.pdf) `2022-05-24 19:45`
    - [北京工业大学2022年“3+3”高考改革省份分省分专业招生计划](http://admissions.bjut.edu.cn/SRGWE5YHHDRYWE33.pdf) `2022-05-24 19:45`
    - 来源：北工大本科招生网招生计划栏目
    - 对照锚点：
      - [招生计划-北工大本科招生网](http://admissions.bjut.edu.cn/zsxx/zsjh.htm)
      - [北京工业大学2025年分省分专业招生计划](https://admissions.bjut.edu.cn/dfiles/2025/2025gaigeshengfenjh.pdf) `2025-06-19 10:00`
      - [北京工业大学2025年京外本科普通批分省分专业招生计划 PDF](https://admissions.bjut.edu.cn/dfiles/2025/2025gaigeshengfenjh.pdf)
  - 价值：
    1. 把北工大从“只有 `2025` 学校侧计划栏目锚点”推进到 `2022-2025` 连续学校侧计划时间线。
    2. `2024` 的“高考改革省份分省分专业招生计划”对广西主线尤其有用，因为后续如果继续补北工大广西计划明细，这条是最贴近改革省份口径的正式上年对照。
    3. `2022-2024` 的国家专项 / 非改革 / `3+1+2` / `3+3` 分拆，也让后续比较学校侧计划发布结构变化更容易。

- 新增补齐两条 **中国药科大学 学校侧高校专项计划正式发布锚点**：
  - [中国药科大学2025年高校专项计划招生简章](https://zb.cpu.edu.cn/f2/f4/c9133a127732/page.htm) `2025-05-01`
  - [中国药科大学2024年高校专项计划招生简章](https://zb.cpu.edu.cn/0d/6d/c9133a200045/page.htm) `2024-04-09`
    - 来源：中国药科大学本科招生网招生章程及特殊类型招生办法栏目页
    - 对照锚点：
      - [中国药科大学招生章程及特殊类型招生办法栏目页](http://zjc.cpu.edu.cn/zszcjtslxzsbf/list.htm)
      - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
      - [中国药科大学2024年普通本科招生章程](https://zb.cpu.edu.cn/2b/1f/c9133a207647/page.htm) `2024-06-12`
      - [2025年广西招生计划](http://zb.cpu.edu.cn/2d/1d/c12765a208157/page.htm) `2025-06-23`
  - 价值：
    1. 把中国药科大学从“普通本科章程 + 广西计划列表项”推进到“普通本科 + 高校专项”双类型学校侧正式发布链路。
    2. 对后续比较学校侧专项计划发布节奏与普通计划/章程入口关系更有帮助，也补强了这所目标校的学校侧结构化追踪面。

- 新增补齐一条 **中国药科大学 2025 学校侧分省计划总入口基线**：
  - [2025招生计划](http://zb.cpu.edu.cn/gszszn/list.htm)
    - 已缓存首批列表项统一显示时间：`2025-06-23`
    - 已明确暴露的子页之一：
      - [2025年广西招生计划](http://zb.cpu.edu.cn/2d/1d/c12765a208157/page.htm) `2025-06-23`
    - 同页还已明确暴露多省子页，如：新疆、湖北、陕西、云南、安徽、河北、北京、上海、甘肃、天津、重庆、内蒙古、辽宁等
  - 来源：中国药科大学本科招生网
  - 对照锚点：
    - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
    - [中国药科大学2025年高校专项计划招生简章](https://zb.cpu.edu.cn/f2/f4/c9133a127732/page.htm) `2025-05-01`
  - 价值：
    1. 把中国药科大学从“只有广西单省计划子页”推进到“学校侧分省计划总入口 + 广西子页”的双层计划链路。
    2. 这会让后续继续补抓中国药科大学广西计划、以及比较学校侧分省计划发布结构和省份拆分方式更容易。

- 新增补齐一条 **中国传媒大学 2025 学校侧高校专项计划发布锚点**：
  - [中国传媒大学2025年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2025/0331/c5834a253756/page.htm) `2025-03-31`
    - 来源：中国传媒大学本科招生网招生简章列表页
    - 对照锚点：
      - [中国传媒大学招生简章列表页](https://zhaosheng.cuc.edu.cn/zsjz/list.htm)
      - [中国传媒大学2025年本科招生章程](https://zhaosheng.cuc.edu.cn/2025/0530/c5852a256319/page.htm) `2025-05-30`
      - [中国传媒大学2024年本科招生章程](https://zhaosheng.cuc.edu.cn/2024/0520/c5852a219907/page.htm) `2024-05-24`
  - 价值：
    1. 把中国传媒大学从“普通本科章程时间线”推进到“普通本科章程 + 高校专项计划招生简章”的并行学校侧发布链路。
    2. 这会让后续比较学校侧普通批与专项计划入口的发布时间关系、栏目组织方式和入口变化更容易。

- 新增补齐一组 **中国传媒大学 2024-2025 学校侧特殊类型招生简章链路**：
  - `2025`：
    - [中国传媒大学2025年艺术类本科校考专业招生简章](https://zhaosheng.cuc.edu.cn/_upload/article/files/55/74/b0970a4b4dcaaaad27b830d35d6e/639005be-bc16-4175-8ab1-d2589d5020ca.pdf) `2025-01-03`
    - [中国传媒大学2025年依据台湾地区大学入学考试学科能力测试成绩招收台湾高中毕业生简章](https://zhaosheng.cuc.edu.cn/2024/1206/c5834a246529/page.htm) `2024-12-06`
    - [中国传媒大学2025年招收香港中学文凭考试学生简章](https://zhaosheng.cuc.edu.cn/2024/1118/c5834a245495/page.htm) `2024-11-18`
    - [中国传媒大学2025年招收澳门保送生简章](https://zhaosheng.cuc.edu.cn/2024/1021/c5834a244339/page.htm) `2024-10-21`
  - `2024`：
    - [中国传媒大学2024年依据学测成绩招收台湾地区高中毕业生简章](https://zhaosheng.cuc.edu.cn/2024/0204/c5834a216432/page.htm) `2024-02-04`
    - [中国传媒大学2024年艺术类本科招生简章](https://zhaosheng.cuc.edu.cn/_upload/article/files/c0/d2/ae48a0e844eb8811a18c889089e6/b3fa9c6e-d160-4bba-8255-fdb086abed4c.pdf) `2024-01-07`
    - [中国传媒大学2024年招收香港中学文凭考试学生简章](https://zhaosheng.cuc.edu.cn/2024/0102/c5834a215110/page.htm) `2024-01-02`
    - 来源：中国传媒大学本科招生网招生简章列表页
    - 对照锚点：
      - [中国传媒大学招生简章列表页](https://zhaosheng.cuc.edu.cn/zsjz/list.htm)
      - [中国传媒大学2025年本科招生章程](https://zhaosheng.cuc.edu.cn/2025/0530/c5852a256319/page.htm) `2025-05-30`
      - [中国传媒大学2025年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2025/0331/c5834a253756/page.htm) `2025-03-31`
  - 价值：
    1. 把中国传媒大学从“普通本科章程 + 高校专项计划”推进到“普通本科 + 高校专项 + 艺术类 + 港澳台相关简章”的更完整学校侧特殊类型发布链。
    2. 这会增强后续比较学校侧不同招生类型入口结构、发布时间分布与规则口径变化的能力。

- 新增补齐一组 **中国传媒大学 2026 学校侧特殊类型招生简章链路**：
  - [中国传媒大学2026年艺术类本科校考专业招生简章](https://zhaosheng.cuc.edu.cn/_upload/article/files/f6/31/97e216a64a9a932024f9e18bcb08/d4085223-54d2-40be-8356-8f0a8d49cc24.pdf) `2026-01-17`
  - [中国传媒大学2026年依据台湾地区大学入学考试学科能力测试成绩招收台湾高中毕业生简章](https://zhaosheng.cuc.edu.cn/2025/1212/c5834a265133/page.htm) `2025-12-12`
  - [中国传媒大学2026年招收香港中学文凭考试学生简章](https://zhaosheng.cuc.edu.cn/2025/1110/c5834a262219/page.htm) `2025-11-11`
  - [中国传媒大学2026年招收澳门保送生简章](https://zhaosheng.cuc.edu.cn/2025/1013/c5834a260927/page.htm) `2025-10-15`
    - 来源：中国传媒大学本科招生网招生简章列表页
    - 对照锚点：
      - [中国传媒大学招生简章列表页](https://zhaosheng.cuc.edu.cn/zsjz/list.htm)
      - [中国传媒大学2025年本科招生章程](https://zhaosheng.cuc.edu.cn/2025/0530/c5852a256319/page.htm) `2025-05-30`
      - [中国传媒大学2025年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2025/0331/c5834a253756/page.htm) `2025-03-31`
  - 价值：
    1. 这批条目把中国传媒大学学校侧特殊类型发布链直接推进到了 `2026`，比单纯补更老年份更有时效价值。
    2. 对后续跟踪 `2026` 学校侧入口变化、发布时间顺序和招生类型组织方式尤其有用。

- 新增补齐一组 **东华大学 2017-2025 学校侧艺术类录取分数发布链**：
  - `2025`：
    - [东华大学2025年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2025/1210/c14938a369716/page.htm) `2026-03-30`
  - `2024`：
    - [东华大学2024年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2024/1107/c14938a352944/page.htm) `2025-02-17`
  - `2023`：
    - [东华大学2023年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2023/0713/c14938a328200/page.htm) `2023-07-13`
  - `2022`：
    - [东华大学2022年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2022/0713/c14938a297382/page.htm) `2022-07-13`
  - `2021`：
    - [东华大学2021年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2021/0902/c14938a285220/page.htm) `2021-09-02`
  - `2020`：
    - [东华大学2020年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2020/1026/c14938a263965/page.htm) `2020-10-27`
  - `2019`：
    - [东华大学2019年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2019/1023/c14938a224637/page.htm) `2019-10-23`
  - `2018 / 2017`：
    - [东华大学2018年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2018/0730/c14938a199122/page.htm) `2018-07-30`
    - [东华大学2017年艺术类专业录取情况统计](http://zs.dhu.edu.cn/2018/0730/c14938a199121/page.htm) `2018-07-30`
    - 来源：东华大学本科招生网艺术类专业分数查询栏目
    - 对照锚点：
      - [东华大学艺术类专业分数查询栏目页](http://zs.dhu.edu.cn/yslzyfscx/list.htm)
      - [东华大学2025年各省市录取分数查询（广西物化组）](http://zs.dhu.edu.cn/2026/0227/c25199a371750/page.htm)
      - [东华大学2025年本科招生章程](http://zs.dhu.edu.cn/2025/0522/c9563a361995/page.htm) `2025-05-22`
  - 价值：
    1. 把东华大学从“广西物化组录取分数文章”推进到“学校侧艺术类录取分数长期发布链”，显著扩宽了学校侧分数来源面。
    2. 这让后续比较东华大学不同招生类型的分数发布节奏、栏目结构和入口延续性更容易。

- 新增补齐两组 **东华大学学校侧并行分数发布链**：
  - **内地高中班录取分数统计**：
    - [2025内地高中班录取分数统计](http://zs.dhu.edu.cn/2025/1210/c21850a369723/page.htm) `2026-03-30`
    - [2024内地高中班录取分数统计](http://zs.dhu.edu.cn/2024/1121/c21850a353409/page.htm) `2025-05-09`
    - [2023内地高中班录取分数统计](http://zs.dhu.edu.cn/2023/1110/c21850a333075/page.htm) `2023-11-10`
    - [2022内地高中班录取分数统计](http://zs.dhu.edu.cn/2022/1130/c21850a318932/page.htm) `2022-11-30`
    - [2021内地高中班录取分数统计](http://zs.dhu.edu.cn/2022/0729/c21850a298018/page.htm) `2022-07-29`
    - 栏目页：[东华大学内地高中班录取分数统计栏目](http://zs.dhu.edu.cn/ndgzblnfscx/list.htm)
  - **少数民族预科录取分数查询**：
    - [2025年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2025/1210/c20710a369735/page.htm) `2026-03-30`
    - [2024年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2024/1121/c20710a353406/page.htm) `2025-02-17`
    - [2023年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2023/1110/c20710a333081/page.htm) `2023-11-10`
    - [2022年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2022/1130/c20710a318933/page.htm) `2022-11-30`
    - [2021年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2022/0607/c20710a296391/page.htm) `2022-06-07`
    - [2020年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2021/0622/c20710a282719/page.htm) `2021-06-22`
    - [2019年少数民族预科录取分数查询](http://zs.dhu.edu.cn/2021/0622/c20710a282714/page.htm) `2021-06-22`
    - 栏目页：[东华大学少数民族预科录取分数查询栏目](http://zs.dhu.edu.cn/ssmzykzslnfscx/list.htm)
  - 来源：东华大学本科招生网
  - 对照锚点：
    - [东华大学2025年各省市录取分数查询（广西物化组）](http://zs.dhu.edu.cn/2026/0227/c25199a371750/page.htm)
    - [东华大学艺术类专业分数查询栏目](http://zs.dhu.edu.cn/yslzyfscx/list.htm)
    - [东华大学2025年各类型分省分专业招生计划](http://zs.dhu.edu.cn/2025/0619/c22353a363015/page.htm) `2025-06-19`
  - 价值：
    1. 把东华大学从“艺术类 + 广西物化组”两条分数链，继续扩展成“内地高中班 + 少数民族预科”两条并行学校侧分数发布链，显著增强学校侧多招生类型发布结构的完整度。
    2. 这会让后续比较东华大学不同招生类型的发布时间顺序、栏目组织方式和入口延续性更容易，也更利于判断哪些链路值得后续服务器侧继续深挖。

- 新增补齐一组 **中国传媒大学 2019-2024 学校侧高校专项计划发布链**，并顺手补齐 `2019-2020` 普通招生章程：
  - **高校专项计划招生简章**：
    - [中国传媒大学2024年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2024/0407/c5852a218342/page.htm) `2024-04-08`
    - [中国传媒大学2023年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2023/0406/c5852a203386/page.htm) `2023-04-06`
    - [中国传媒大学2022年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2022/0412/c5852a192437/page.htm) `2022-04-12`
    - [中国传媒大学2021年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2021/0414/c5852a179965/page.htm) `2022-04-12`
    - [中国传媒大学2020年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2020/0507/c5852a170184/page.htm) `2020-05-07`
    - [中国传媒大学2019年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2019/0417/c5852a169569/page.htm) `2019-04-17`
  - **普通招生章程补齐**：
    - [中国传媒大学2020年招生章程](https://zhaosheng.cuc.edu.cn/2020/0706/c5852a171649/page.htm) `2020-07-06`
    - [中国传媒大学2019年招生章程](https://zhaosheng.cuc.edu.cn/2019/0606/c5852a166474/page.htm) `2019-06-06`
  - 来源：[中国传媒大学招生章程栏目页](https://zhaosheng.cuc.edu.cn/zszc/list.htm)
  - 对照锚点：
    - [中国传媒大学2025年本科招生章程](https://zhaosheng.cuc.edu.cn/2025/0530/c5852a256319/page.htm) `2025-05-30`
    - [中国传媒大学2025年高校专项计划招生简章](https://zhaosheng.cuc.edu.cn/2025/0331/c5834a253756/page.htm) `2025-03-31`
    - 已登记的 `2024-2026` 艺术类、港澳台特殊类型招生简章链
  - 价值：
    1. 把中国传媒大学从“2021-2025 普通章程 + 2025 高校专项 + 2024-2026 特殊类型简章”继续扩展成更完整的 `2019-2025` 普通章程链和 `2019-2025` 高校专项链。
    2. 这让后续比较中国传媒大学学校侧普通批与高校专项两条并行发布链的发布时间、栏目组织方式和入口延续性更容易，也增强了对 `2026` 入口变化的基线覆盖。

- 新增补齐一组 **中国药科大学 2022-2023 学校侧特殊类型招生发布链**：
  - **高校专项计划招生简章**：
    - [中国药科大学2023年高校专项计划招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=193166) `2023-10-30`
    - [中国药科大学2022年高校专项计划招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=176447) `2022-11-09`
  - **外语类保送生招生简章**：
    - [中国药科大学2023年外语类保送生招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=193163) `2023-10-30`
    - [中国药科大学2022年外语类保送生招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=176446) `2022-11-09`
  - **高水平运动队招生简章**：
    - [中国药科大学2023年高水平运动队招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=193165) `2023-10-30`
    - [中国药科大学2022年高水平运动队招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=176445) `2022-11-09`
  - **高水平艺术团招生简章**：
    - [中国药科大学2023年高水平艺术团招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=193164) `2023-10-30`
    - [中国药科大学2022年高水平艺术团招生简章](http://zjc.cpu.edu.cn/_redirect?siteId=260&columnId=11258&articleId=176444) `2022-11-09`
  - 来源：[中国药科大学招生章程及特殊类型招生办法栏目页](http://zjc.cpu.edu.cn/zszcjtslxzsbf/list.htm)
  - 对照锚点：
    - [中国药科大学2025年普通本科招生章程](https://zb.cpu.edu.cn/6d/ae/c9133a224686/page.htm) `2025-05-30`
    - [中国药科大学2025年高校专项计划招生简章](https://zb.cpu.edu.cn/f2/f4/c9133a127732/page.htm) `2025-05-01`
    - [2025招生计划](http://zb.cpu.edu.cn/gszszn/list.htm) `2025-06-23`
  - 价值：
    1. 把中国药科大学从“普通章程 + 广西计划 + 2024-2025 高校专项”推进到更完整的 `2022-2025` 特殊类型发布链，补足了保送生、高水平运动队和高水平艺术团这些并行栏目。
    2. 这会让后续比较中国药科大学学校侧不同招生类型的发布时间、栏目结构和入口延续性更容易，也增强了学校侧基线的完整度。

- 新增补齐一条 **中国传媒大学学校侧台湾地区招生更早基线**：
  - [中国传媒大学2020年依据学测成绩招收台湾地区高中毕业生简章](https://zhaosheng.cuc.edu.cn/2020/0304/c5852a166475/page.htm) `2020-03-04`
  - 来源：[中国传媒大学招生章程栏目页](https://zhaosheng.cuc.edu.cn/zszc/list.htm)
  - 对照锚点：
    - [中国传媒大学2024年依据学测成绩招收台湾地区高中毕业生简章](https://zhaosheng.cuc.edu.cn/2024/0204/c5834a216432/page.htm) `2024-02-04`
    - [中国传媒大学2025年依据台湾地区大学入学考试学科能力测试成绩招收台湾高中毕业生简章](https://zhaosheng.cuc.edu.cn/2024/1206/c5834a246529/page.htm) `2024-12-06`
    - [中国传媒大学2026年依据台湾地区大学入学考试学科能力测试成绩招收台湾高中毕业生简章](https://zhaosheng.cuc.edu.cn/2025/1212/c5834a265133/page.htm) `2025-12-12`
  - 价值：
    1. 这把中国传媒大学学校侧台湾地区招生发布链直接往前补到了 `2020`，让这条特殊类型时间线不再只覆盖近两三年。
    2. 对后续比较中传港澳台相关入口的发布时间和栏目延续性更有帮助。

- 新增确认一个 **江南大学 admissions3 站点的明确访问门槛**：
  - 计划页：`http://admission3.jiangnan.edu.cn/pc/recruitstudents/plan`
  - 历史分数页：`http://admission3.jiangnan.edu.cn/pc/historyScore/nonArt`
  - 前端 JS 已公开暴露接口族：
    - `/front/recruitmentPlan/getQuery`
    - `/front/recruitmentPlan/getProvinceQuery`
    - `/front/recruitmentPlan/getList`
    - `/front/historyScore/getQuery`
    - `/front/historyScore/getNotArtProvinceQuery`
    - `/front/historyScore/getList`
  - `2026-05-17` 服务器侧新增验证：
    1. 先暖计划页主页会话并获取 cookie；
    2. 再携带 `Referer`、`Origin`、`X-Requested-With` 和同域 cookie 回放 `getList` 接口；
    3. 页面和接口都统一返回 `483`，正文明确提示“该系统仅限校内访问，非校园网用户请通过校园资源VPN进行访问”，并跳转 `https://webvpn.jiangnan.edu.cn/`。
  - 价值：
    1. 这把江南大学从“尚未完成参数回放”明确升级为“WEBVPN / 校园网门槛阻塞”。
    2. 后续如果没有校园网或 WEBVPN 入口，就不值得继续在这条线上反复猜参数和头信息。

- 新增确认一个 **北京化工大学主站可复用本科招生入口锚点**：
  - [本科生招生](http://www.buct.edu.cn/2021/0507/c11438a151254/page.htm) `2021-05-07 09:21:57`
  - 来源：北京化工大学官网
  - 服务器侧新增验证：
    1. 先从主站本科招生栏目页确认学校自有文章服务 `/_wp3services/generalQuery?queryObj=articles`；
    2. 再以 `siteId=2`、`columnId=11438` 服务器侧直调文章服务；
    3. 返回唯一正式文章 `本科生招生`，并给出精确发布时间 `2021-05-07 09:21:57.0` 和正文 URL。
  - 正文锚点：
    - `高考统招`
    - `保送生`
    - `高水平运动队`
    - `高水平艺术团`
    - `第二学士学位`
    - `高校专项“圆梦计划”`
    - `台湾高中毕业生`
  - 价值：
    1. 这把北京化工大学从“只有主站壳页和失效 goto 门户”推进到“已确认存在带精确时间的学校侧本科招生正式入口页”。
    2. 后续继续补北化的计划、分数和招生政策正文时，可以优先沿主站文章服务与这些正式栏目走，不再回旧 `goto` AJAX 路线盲打。
  - 同轮补充结论：
    1. 主站文章服务中，`高考统招` 栏目 `11442` 以及 `保送生` `11443`、`高水平运动队` `11444`、`高水平艺术团` `11445`、`第二学士学位` `11446`、`高校专项“圆梦计划”` `11447`、`台湾高中毕业生` `11448` 当前都返回 `total: 0`。
    2. 这意味着北京化工大学主站这些本科子栏目前阶段更像“静态栏目壳页”，短期不再把它们当作能直接吐出招生正文列表的低成本突破口。
  - `2026-05-18` 服务器侧新增补充：
    1. 继续直探主栏目路径 `https://www.buct.edu.cn/zsjy/11437/list.htm` 时，当前已不再返回正常栏目页，而是直接给出“提示：访问地址无效，zsjy/11437找不到对应的栏目！”错误页；
    2. 但同一轮再沿本地缓存页里暴露的学校侧子路径逐个复核后，以下七条子页都仍稳定返回 `200`，并在源码中明确回写对应标题与 `columnId`：
       - `https://www.buct.edu.cn/gktz/list.htm` → `高考统招` → `columnId=11442`
       - `https://www.buct.edu.cn/bss/list.htm` → `保送生` → `columnId=11443`
       - `https://www.buct.edu.cn/gspydd/list.htm` → `高水平运动队` → `columnId=11444`
       - `https://www.buct.edu.cn/gspyst/list.htm` → `高水平艺术团` → `columnId=11445`
       - `https://www.buct.edu.cn/dexsxw/list.htm` → `第二学士学位` → `columnId=11446`
       - `https://www.buct.edu.cn/gxzxwymjhw/list.htm` → `高校专项“圆梦计划”` → `columnId=11447`
       - `https://www.buct.edu.cn/twgzbys/list.htm` → `台湾高中毕业生` → `columnId=11448`
    3. 再以 `高考统招` 子页 `https://www.buct.edu.cn/gktz/list.htm` 为样本继续下钻后，已确认它内嵌的官方文章服务仍是 `/_wp3services/generalQuery?queryObj=articles`，但页面脚本当前只拿 `siteId=2`、`columnId=11442`、`scope=0`、`title/imgPath` 去查背景图数据；按这组内嵌参数直调服务后返回 `total=0`、`data=[]`，结果已缓存到 `raw_data/official_followup/beijing_huagong_211/buct_gktz_scope0_query_20260518.json`。
    4. 这说明北化这批活子页当前更像“背景图/栏目壳页”，短探尚未直接抽到正文级文章链接，但它们已经构成比失效主栏目页更可靠的学校侧后续入口集；批量探测结果已缓存到 `raw_data/official_followup/beijing_huagong_211/buct_child_pages_20260518.json`。
  - 价值：
    1. 这把北京化工大学从“主栏目和旧 goto 都不可靠”的模糊状态，推进到“主栏目路径已漂移失效，但七条学校侧子页壳页仍活”的更清晰结构。
    2. 这也进一步排除了一个低成本误判点：至少 `高考统招` 子页当前并不是现成文章列表页，不能再按“子页一活就该有正文”去期待直接落账。
    3. 后续如果继续补北化，优先级已经很明确：从这七条活子页继续找其他正文和服务钩子，而不是回到 `zsjy/11437/list.htm` 或旧 `goto` 门户重复探测。

- 新增澄清一个 **中国矿业大学（北京）本科招生主站入口与链路阻塞口径**：
  - 学校主站入口：[招生就业-中国矿业大学（北京）](https://www.cumtb.edu.cn/zsjy.htm)
  - 学校侧本科入口：`http://zb.cumtb.edu.cn`
  - `2026-05-17` 服务器侧新增验证：
    1. 主站 `招生就业` 页面可稳定访问，页内多处明确锚定 `本科生招生 -> http://zb.cumtb.edu.cn`；
    2. 该本科招生子域当前从服务器直连返回 `403`；
    3. 同轮再次直抓主站 `招生就业` 页 HTML，确认页面本体只是导航壳页，未见稳定可见的发布日期；
    4. 因此，这条线已从“只有研招弱证据、尚未确认本科入口”升级为“本科主站入口已确认，但当前为链路型阻塞；主站壳页本身还不足以单独入账正式来源”。
  - 价值：
    1. 后续不再把中国矿业大学（北京）当作“入口未确认”的模糊学校线反复重试。
    2. 如果后面网络条件变化或更换出口，优先重试 `zb.cumtb.edu.cn` 本科域，而不是继续围绕研招缓存页打转。
    3. 同时也不再把 `https://www.cumtb.edu.cn/zsjy.htm` 这类无日期导航壳页误判成可直接登记的学校侧正式来源。

- 新增澄清一个 **南昌大学学校侧招生计划 / 历年分数 query shell 入口已确认但真实 param 基准路径未解开** 的口径：
  - 学校主站入口：[本科生招生-南昌大学](https://www.ncu.edu.cn/zsjy/bkszs.htm)
  - 主站页内直接暴露的学校侧入口：
    - `https://zjc.ncu.edu.cn/zs/zsw/zsjh.html`
    - `https://zjc.ncu.edu.cn/zs/zsw/lnfs.html`
  - `2026-05-17` 服务器侧新增验证：
    1. 主站 `本科生招生` 页可稳定访问，页内明确给出 `招生计划` 与 `历年分数` 两条学校侧查询页；
    2. 两条学校侧查询页都稳定返回 `200`，并在脚本中暴露 `f/ajax_zsjh_param`、`f/ajax_zsjh`、`f/ajax_zyjs_zy` 与 `f/ajax_lnfs_param`、`f/ajax_lnfs` 等同家族接口签名；
    3. 继续按最直观的三种基准路径回放参数接口：
       - `https://zjc.ncu.edu.cn/f/ajax_zsjh_param`
       - `https://zjc.ncu.edu.cn/zs/f/ajax_zsjh_param`
       - `https://zjc.ncu.edu.cn/zs/zsw/f/ajax_zsjh_param`
       都返回 `404`，说明页面本体已确认，但真实接口基准路径还需要再解析。
    4. 同轮继续从 `init.js` 中提取到静态壳页候选：
       - `https://zjc.ncu.edu.cn/static/front/nxtc/basic/html_web/zsjh.html`
       - `https://zjc.ncu.edu.cn/static/front/nxtc/basic/html_web/lnfs.html`
       但这两条候选静态壳页也都返回 `404`，说明当前更像是主站 wrapper 仍在、旧 shell 路径已漂移。
    5. 继续下钻 `zsjh.html` 的内联脚本后，已确认页面实际请求方式就是 `POST $.url('f/ajax_zsjh_param')` 与 `POST $.url('f/ajax_zsjh')`；
    6. 再按页面自己的 `XHR + POST` 口径，分别把 `ajax_zsjh_param` 与 `ajax_zsjh` 回放到 `https://zjc.ncu.edu.cn/f/*`、`https://zjc.ncu.edu.cn/zs/f/*`、`https://zjc.ncu.edu.cn/zs/zsw/f/*` 三组最可能候选基址后，六次请求都统一返回 `404`。
    7. 同轮继续回看 `zsjh.html` 页面本体，确认页面并非纯空模板：筛选区 HTML 已直接内嵌完整省份枚举，包含 `北京 / 天津 / 河北 / ... / 广西 / ... / 澳门` 等 `data-value` 项，说明前端至少已预置一套可用的省份维度筛选数据，只是 `$.url()` 背后的真实重写基址仍未露出。
    8. 再沿学校侧 `招生政策` 列表页 `https://zjc.ncu.edu.cn/zs/f/newsCenter/articles/c16ba2eb52844a43a53a091335b20626` 继续下钻，已确认两条正式招生章程文章：
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/ab3072836b6a41df98f7763cb41ab157` 《南昌大学2025年全日制普通本科招生章程》，页面发布时间 `2025-05-13`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/d7ee1bc7375b42b49df1704ac0ee6fd0` 《南昌大学2024年本科招生章程》，页面发布时间 `2024-05-15`
       这说明南昌大学不只是 query shell 入口已露出，学校侧招生章程正式页时间线也已经开始补齐。
    9. 同轮继续利用页面自带翻页逻辑 `?pageNo=...&pageSize=10` 深挖 `招生政策` 列表分页，并逐页单独复核正文日期后，又确认了多条更早年份的正式章程页：
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/dbf7cf90b7a04d1091becbabef9ab758` 《南昌大学2022年招生章程》，页面发布时间 `2022-05-14`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/84d906228d8845f2bb4bc303ac8c6cf0` 《南昌大学2021年招生章程》，页面发布时间 `2021-06-23`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/22dfe8e41271478f8472780a831a4e84` 《南昌大学2019年招生章程》，页面发布时间 `2019-06-14`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/f4c7359b7a0d4c33b28f25d5e01d8e58` 《南昌大学2018年招生章程》，页面发布时间 `2018-06-05`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/b5de3a67d7fa4f47919b9904930637cf` 《南昌大学2016年招生章程》，页面发布时间 `2016-06-01`
       当前 live policy pagination 中尚未直接看到 `2023` 与 `2020` 的普通本科章程页，因此这条学校侧章程时间线已经明显拉长，但暂不表述为连续年份序列。
    10. 同轮再沿同一 `招生政策` 栏目向特殊类型条目继续下钻，并逐页单独复核正文日期后，又确认了一组学校侧 `2025-2026` 特殊类型招生简章：
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/a1c35473ba9b4265ba41a2c345c593a6` 《南昌大学2026年保送运动员招生简章》，页面发布时间 `2026-01-15`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/6766a5cec66546a0bcc72f9481cbcda0` 《南昌大学2026年运动训练专业招生简章》，页面发布时间 `2026-01-15`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/152eb901866244fcb1d6078948bb7f8f` 《南昌大学2025年第二学士学位招生简章》，页面发布时间 `2025-06-06`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/eafd3e4c5b5f498997db55e3c699386d` 《南昌大学2025年高水平运动队招生简章》，页面发布时间 `2025-01-26`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/ea09327287fb4500a32c24237d28659c` 《南昌大学2025年运动训练专业招生简章》，页面发布时间 `2025-01-17`
       - `https://zjc.ncu.edu.cn/zs/f/newsCenter/article/8cd945bfb2384433a08d608e277bedbb` 《南昌大学2025年保送运动员招生简章》，页面发布时间 `2025-01-16`
       这说明南昌大学学校侧 `招生政策` 栏并不只是普通本科章程列表，而是已经形成了普通本科章程 + 特殊类型简章并行的正式发布链。
  - 价值：
    1. 这把南昌大学从“只有学校主站和本科招生壳页”推进到“学校侧计划/分数 query shell 已确认、页面内联 POST 目标已读出、且多年份普通本科章程基线与 2025-2026 特殊类型发布链都已落地”的更具体状态。
    2. 这也把阻塞口径从泛化的“路径漂移”收紧为“学校侧正式发布链已经很丰富，但连按正确方法回放到三组候选基址仍统一 404”的更精确状态。
    3. 同时，页面内嵌省份筛选值也说明这条线值得继续围绕真实接口重写层深挖，而不是直接判死。
    4. 后续继续补抓时，优先解析 `$.url()` 背后的隐藏重写基址或反向代理层，而不是再重复从主站重找入口，也不再把 `static/front/nxtc/basic/html_web` 这组旧静态路径当成新的高优先级突破口。

- 新增补齐一个 **延边大学学校侧本科招生入口链**：
  - 招生就业处首页：[招生就业处](https://zsjy.ybu.edu.cn/)
  - 学校侧本科招生网：[延边大学招生网](https://zsb.ybu.edu.cn/)
  - 学校侧招生计划页：[招生计划](https://zsb.ybu.edu.cn/bkzn/zsjh.htm)
  - 学校侧分数 / 录取查询入口：
    - `https://gklqcx.ybu.edu.cn/recruit`
    - `https://gklqcx.ybu.edu.cn/admission`
  - `2026-05-17` 服务器侧新增验证：
    1. 招生就业处首页可稳定访问，页内明确暴露 `本科招生网 / 历年分数线 / 高考录取查询` 三条学校侧入口；
    2. `https://zsb.ybu.edu.cn/` 可稳定访问，首页可见 `招生计划`、`招生政策` 等栏目；
    3. 同一首页可见带日期的正式通知页 [关于开通延边大学2025年高考录取查询系统的通知](https://zsb.ybu.edu.cn/info/1009/1697.htm)，发布时间为 `2025年07月09日`；
    4. 同一首页还直接挂出 [延边大学2026年招生章程](https://zsb.ybu.edu.cn/info/1010/1723.htm) 与 [延边大学2025年招生章程](https://zsb.ybu.edu.cn/info/1010/1663.htm) 等正式文章；本轮服务器侧复核确认其页面日期分别为 `2026年04月27日` 与 `2025年05月20日`；
    5. 继续直抓 [延边大学2024年招生章程](https://zsb.ybu.edu.cn/info/1010/1603.htm) 与 [延边大学2023年招生章程](https://zsb.ybu.edu.cn/info/1010/1553.htm) 正文页后，确认其页面日期分别为 `2024年05月08日` 与 `2023年05月19日`；
    6. 再从招生章程列表页继续下钻，确认 [延边大学2022年招生章程](https://zsb.ybu.edu.cn/info/1010/1483.htm)、[延边大学2021年招生章程](https://zsb.ybu.edu.cn/info/1010/1361.htm)、[延边大学2020年招生章程](https://zsb.ybu.edu.cn/info/1010/1303.htm) 正文页页面日期分别为 `2022年06月02日`、`2021年05月17日`、`2021年01月06日`，至此学校侧章程时间线已连成 `2020-2026` 七年；
    7. 同轮继续从首页与专题栏目页补抓特殊类型正式发布页后，又确认了四条学校侧特殊类型招生简章：
       - `https://zsb.ybu.edu.cn/info/1013/1714.htm` 《延边大学2026年保送录取优秀运动员招生简章》，页面发布时间 `2026年01月17日 10:07`
       - `https://zsb.ybu.edu.cn/info/1013/1713.htm` 《延边大学2026年运动训练专业招生简章》，页面发布时间 `2025年12月16日 13:51`
       - `https://zsb.ybu.edu.cn/info/1013/1654.htm` 《延边大学2025年运动训练专业招生简章》，页面发布时间 `2024年12月26日 19:32`
       - `https://zsb.ybu.edu.cn/info/1086/1688.htm` 《延边大学2025年第二学士学位招生简章》，页面发布时间 `2025年06月09日 10:53`
       这说明延边大学学校侧招生网不仅有普通本科章程时间线，也已经形成了清晰的特殊类型正式发布链。
    8. 同轮继续从首页与艺术类专题栏目补抓后，又确认了四条学校侧艺术类正式通知页：
       - `https://zsb.ybu.edu.cn/info/1012/1703.htm` 《关于延边大学2026年艺术类专业省统考子科类对照表的说明》，页面发布时间 `2025年10月27日 17:39`
       - `https://zsb.ybu.edu.cn/info/1012/1695.htm` 《关于延边大学2025年艺术类专业省统考子科类对照表的说明》，页面发布时间 `2025年06月23日 17:39`
       - `https://zsb.ybu.edu.cn/info/1012/1573.htm` 《关于延边大学2024年艺术类专业省统考子科类对照表的说明》，页面发布时间 `2023年10月20日 10:38`
       - `https://zsb.ybu.edu.cn/info/1012/1534.htm` 《关于公示延边大学2023年艺术类校考合格线及拟合格名单的通知》，页面发布时间 `2023年03月20日 09:37`
       这说明延边大学学校侧艺术类招生也已形成一条可追溯的正式通知链，而不只是散落在首页的单条公告。
    9. 同轮继续从首页与第二学士学位专题栏目补抓后，又确认了三条学校侧流程通知页：
       - `https://zsb.ybu.edu.cn/info/1009/1696.htm` 《关于公布延边大学高考录取期间咨询热线的通知》，页面发布时间 `2025年07月01日 08:08`
       - `https://zsb.ybu.edu.cn/info/1086/1694.htm` 《关于公示延边大学2025年第二学士学位补充拟录取名单的通知》，页面发布时间 `2025年06月23日 10:46`
       - `https://zsb.ybu.edu.cn/info/1086/1693.htm` 《关于公示延边大学2025年第二学士学位拟录取名单的通知》，页面发布时间 `2025年06月19日 17:31`
       这说明延边大学学校侧招生网还具备一条清晰的招生流程通知链，不只是规则页和专项招生简章。
    10. 同轮继续下钻 `招生计划` 页 `https://zsb.ybu.edu.cn/bkzn/zsjh.htm` 后，又确认该页并非空壳，而是通过省份 image map 直接挂出各省计划图；其中 `广西` 对应的正式图源为 `https://zsb.ybu.edu.cn/images/2025/guangxi.jpg`，服务器侧验证其返回 `200 image/jpeg`、大小 `893527` 字节，并已缓存到 `raw_data/official_followup/yanbian_daxue_211/ybu_2025_guangxi_plan.jpg`。这使延边大学从“学校侧通知链较完整”进一步推进到“已落地一条广西定向计划图源”。
    11. `https://gklqcx.ybu.edu.cn/recruit` 与 `https://gklqcx.ybu.edu.cn/admission` 当前从服务器直连都返回 `403`。
  - 价值：
    1. 这把延边大学从“只有招生就业站点 discovery 命中”推进到“学校侧本科招生网与分数/录取查询入口链已确认”的更具体状态。
    2. 项目现在不仅有一条带精确日期的延边大学官方招生通知可入账，还补齐了 `2020-2026` 连续七年的学校侧招生章程正式页、`2025-2026` 特殊类型招生简章链、`2023-2026` 艺术类正式通知链、`2025` 招生流程通知链，以及一条已经缓存落地的 `2025 广西计划图源`，学校侧规则、专项、流程与广西定向计划证据都已经明显变厚。
    3. 后续可优先围绕这张 `广西` 计划图做结构化尝试或人工核表，同时继续低成本回看招生网内 `招生计划 / 招生政策 / 专业导航` 的新正文，而不必再把延边大学当成只有查询口的弱证据学校。

- 新增补齐一个 **云南大学学校侧计划 / 分数 / 录取 query shell 入口链**：
  - 本科招生网首页：[云南大学本科招生网](http://zsb.ynu.edu.cn/)
  - 学校侧三条 query shell：
    - `https://zsfz.ynu.edu.cn/zsw/zsjh.html`
    - `https://zsfz.ynu.edu.cn/zsw/lnfs.html`
    - `https://zsfz.ynu.edu.cn/zsw/lqcx.html`
  - `2026-05-17` 服务器侧新增验证：
    1. 本科招生网首页可稳定访问，导航与首页快捷入口都直接暴露 `招生计划 / 往年招生 / 录取信息查询` 三条学校侧查询页；
    2. 三条 query shell 页面本体都稳定返回 `200`；
    3. 其中 `https://zsfz.ynu.edu.cn/zsw/zsjh.html` 暴露 `f/ajax_zsjh_param`，`https://zsfz.ynu.edu.cn/zsw/lnfs.html` 暴露 `f/ajax_lnfs_param`，`https://zsfz.ynu.edu.cn/zsw/lqcx.html` 暴露 `f/ajax_lqcx`；
    4. 继续用服务器侧同域请求头回放后，`f/ajax_zsjh_param` 与 `f/ajax_lnfs_param` 当前都返回 `403`，`f/ajax_lqcx` 当前返回 `404`。
  - 价值：
    1. 这把云南大学从“只有学校本科招生网 discovery 命中”推进到“学校侧计划 / 分数 / 录取查询入口链已确认”的更具体状态。
    2. 项目现在已经可以明确把云南大学纳入“入口已确认、接口层阻塞待解”的学校侧查询家族，不再把它当成单纯待发现站点处理。
    3. 这个判断后来被证明还是偏保守，因为同站 `tplt.js` 里实际还藏着 `POST /f/ajax_get_csrfToken (n=3)` 的 token 链，不能只按“空回放 403”下结论。

- 新增把 **云南大学学校侧 query shell** 从“接口层阻塞”升级为“计划 + 分数 API 已打通”的口径：
  - 学校侧查询页：
    - `https://zsfz.ynu.edu.cn/zsw/zsjh.html`
    - `https://zsfz.ynu.edu.cn/zsw/lnfs.html`
  - `2026-05-18` 服务器侧新增验证：
    1. 继续抓取 live `https://zsfz.ynu.edu.cn/static/front/ynu/basic/js/tplt.js` 后，已确认云南大学与 USTB 同族，真实前端顺序并不是直接回放 `f/ajax_zsjh_param` / `f/ajax_lnfs_param`，而是先 `POST /f/ajax_get_csrfToken (n=3)`，再把返回 token 串拆分后轮转写入 `Csrf-Token` 请求头；
    2. 再按这个真实顺序回放后，`https://zsfz.ynu.edu.cn/f/ajax_zsjh_param` 与 `https://zsfz.ynu.edu.cn/f/ajax_lnfs_param` 都成功返回 `200` 和完整参数表；
    3. 继续定向回放 `广西 + 2025 + 物理类/历史类 + 普通本科批` 后，计划链 `f/ajax_zsjh` 与分数链 `f/ajax_lnfs` 都成功直返正式数据：
       - 计划侧：`物理类` 总计划 `115`、专业行 `45` 条；`历史类` 总计划 `26`、专业行 `15` 条；
       - 分数侧：`物理类` 最低分 `443`、最低位次 `102067`、平均分 `556.44`、最高分 `606`、专业行 `45` 条；`历史类` 最低分 `569`、最低位次 `3691`、平均分 `577.81`、最高分 `596`、专业行 `15` 条。
    4. 参数响应、四份原始 JSON 与两份合并 CSV 已缓存到：
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_zsjh_param.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_wuli_plan.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_lishi_plan.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_lnfs_param.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_wuli_score.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_lishi_score.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_score_rows.csv`
    5. 同链继续回放 `广西 + 2024 + 物理类/历史类 + 普通本科批` 与 `广西 + 2023 + 理工/文史 + 普通本科批` 后，计划链与分数链都继续稳定命中更早年份正式数据：
       - `2024` 计划侧：`物理类` 总计划 `115`、专业行 `34` 条；`历史类` 总计划 `27`、专业行 `15` 条；
       - `2024` 分数侧：`物理类` 最低分 `569`、最低位次 `16991`、平均分 `582.01`、最高分 `606`、专业行 `34` 条；`历史类` 最低分 `563`、最低位次 `4437`、平均分 `585.48`、最高分 `602`、专业行 `15` 条；
       - `2023` 计划侧：`理工` 总计划 `82`、专业行 `31` 条；`文史` 总计划 `28`、专业行 `15` 条；
       - `2023` 分数侧：`理工` 最低分 `545`、最低位次 `17026`、平均分 `558.5`、最高分 `585`、专业行 `31` 条；`文史` 最低分 `590`、最低位次 `2048`、平均分 `595.04`、最高分 `605`、专业行 `15` 条。
    6. 这轮继续拆出的跨年 bundle、八份拆分 JSON 与两份跨年汇总 CSV 已缓存到：
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2023_2024_guangxi_bundle.json`
       - `raw_data/official_followup/yunnan_daxue_211/plan_2024_wuli.json`
       - `raw_data/official_followup/yunnan_daxue_211/plan_2024_lishi.json`
       - `raw_data/official_followup/yunnan_daxue_211/plan_2023_ligong.json`
       - `raw_data/official_followup/yunnan_daxue_211/plan_2023_wenshi.json`
       - `raw_data/official_followup/yunnan_daxue_211/score_2024_wuli.json`
       - `raw_data/official_followup/yunnan_daxue_211/score_2024_lishi.json`
       - `raw_data/official_followup/yunnan_daxue_211/score_2023_ligong.json`
       - `raw_data/official_followup/yunnan_daxue_211/score_2023_wenshi.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2023_2024_guangxi_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2023_2024_guangxi_score_rows.csv`
    7. 同轮再沿 live `tplt.js` 细看后，发现这类站点除了 `POST /f/ajax_get_csrfToken (n=3)` 之外，还必须补齐 `X-Requested-Time`，并把每次响应头返回的 `Csrf-Token` 继续压回队列，才能稳定复现前端的真实请求链；按这个更完整口径回放后，又继续命中 `2022` 年广西普通类数据：
       - `2022` 计划侧：`理工` 总计划 `81`、专业行 `27` 条；`文史` 总计划 `29`、专业行 `15` 条；
       - `2022` 分数侧：`理工` 最低分 `525`、最低位次 `22445`、平均分 `560.75`、最高分 `584`、专业行 `27` 条；`文史` 最低分 `565`、最低位次 `4612`、平均分 `586.17`、最高分 `605`、专业行 `15` 条。
    8. 对应原始 bundle、四份拆分 JSON、当年 CSV 与新的 `2022-2024` 跨年汇总 CSV 已缓存到：
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_guangxi_bundle.json`
       - `raw_data/official_followup/yunnan_daxue_211/plan_2022_ligong.json`
       - `raw_data/official_followup/yunnan_daxue_211/plan_2022_wenshi.json`
       - `raw_data/official_followup/yunnan_daxue_211/score_2022_ligong.json`
       - `raw_data/official_followup/yunnan_daxue_211/score_2022_wenshi.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_guangxi_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_guangxi_score_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2024_guangxi_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2024_guangxi_score_rows.csv`
    9. 同轮继续按完全相同的链路再回放 `2021` 年广西 `理工 / 文史 + 普通本科批` 时，接口层并没有重新变成 `403` 或 `404`，而是统一返回 `state=1 / msg=操作成功`，但
       - 计划侧 `zsjhTotal` 与 `zsjhList` 都为空；
       - 分数侧 `zsSsgradeList` 与 `sszygradeList` 也都为空。
       对应空结果 bundle 已缓存到 `raw_data/official_followup/yunnan_daxue_211/ynu_2021_guangxi_bundle.json`。
  - 价值：
    1. 这把云南大学从“学校侧规则时间线很完整但 query shell 阻塞”的状态，直接升级成“学校侧广西计划 + 分数 API 已落地”的实数源。
    2. 现在这条线已经从 `2025` 单年突破扩展成 `2022-2025` 连续四年的广西普通类计划 + 分数时间序列，后续做 `2026` 对照时有了更稳的学校侧基线。
    3. 这也进一步说明同族站点不能只按“空回放 + cookie”去判死，`tplt.js` 里 `csrf` + `X-Requested-Time` + 响应头 token 轮转三件套一起满足，才是更接近真实前端的低成本解法。
    4. 同时这轮也把当前公开下界收紧得更清楚：至少在学校侧这条普通类 API 线上，`2021` 广西同组合已经是“空成功包”，所以短期更值得把精力放到别的学校或别的分支，而不是重复盲打云大 `2021`。

- 新增补齐一组 **云南大学学校侧 `2022-2025` 广西高校专项计划 + 分数并行时间线**：
  - 计划接口：`https://zsfz.ynu.edu.cn/f/ajax_zsjh`
  - 分数接口：`https://zsfz.ynu.edu.cn/f/ajax_lnfs`
  - `2026-05-18` 服务器侧新增验证：
    1. 继续沿与普通本科批完全相同的真链 `POST /f/ajax_get_csrfToken (n=3) -> X-Requested-Time -> 响应头 Csrf-Token 轮转 -> f/ajax_zsjh / f/ajax_lnfs` 回放参数图中已公开的 `高校专项` 组合；
    2. 计划链与分数链都整段命中 `2022-2025` 连续四年广西高校专项数据：
       - `2025` 计划：`物理类` 总计划 `2`（生物科学类）、`历史类` 总计划 `1`（汉语言文学）；
       - `2025` 分数：`物理类` 最低分 `539`、最低位次 `30313`；`历史类` 最低分 `587`、最低位次 `2101`；
       - `2024` 计划：`物理类` 总计划 `1`、`历史类` 总计划 `1`；
       - `2024` 分数：`物理类` 最低分 `548`、最低位次 `26399`；`历史类` 最低分 `586`、最低位次 `2197`；
       - `2023` 计划：`理工` 总计划 `1`（生物科学类）、`文史` 总计划 `1`（公共事业管理）；
       - `2023` 分数：`理工` 最低分 `556`、最低位次 `13816`；`文史` 最低分 `566`、最低位次 `4680`；
       - `2022` 计划：`理工` 总计划 `1`、`文史` 总计划 `1`；
       - `2022` 分数：`理工` 最低分 `560`、最低位次 `11536`；`文史` 最低分 `579`、最低位次 `3007`。
    3. 对应 bundle、分年 JSON、当年行级 CSV 与跨年汇总 CSV 已缓存到 `raw_data/official_followup/yunnan_daxue_211/ynu_20250518_gaoxiaozhuanxiang_bundle.json`、各 `ynu_20xx_guangxi_*_gaoxiaozhuanxiang_*.json` / `_rows.csv` 文件，以及 `ynu_2022_2025_gaoxiaozhuanxiang_plan_rows.csv` 和 `ynu_2022_2025_gaoxiaozhuanxiang_score_rows.csv`。
  - 价值：
    1. 这把云南大学从“只有 `2022-2025` 广西普通本科批时间线”推进到“普通本科批 + 高校专项”两条并行的学校侧广西 API 时间线。
    2. 后续更值得继续沿同一真链扩展 `少数民族预科` 与 `中外合作办学普通专业`，而不是再回头重试已经坐实为空的 `2021` 普通类。

- 新增补齐一组 **云南大学学校侧广西 `中外合作办学普通专业 + 少数民族预科` 并行子线**：
  - 主入口仍为：
    - `https://zsfz.ynu.edu.cn/zsw/zsjh.html`
    - `https://zsfz.ynu.edu.cn/zsw/lnfs.html`
  - `2026-05-18` 服务器侧新增验证：
    1. 沿完全相同的 live `csrf(n=3) + X-Requested-Time + response-header Csrf-Token` 真链继续回放参数图中已暴露的广西平行组合后，又新增命中：
       - `2025` 广西 `物理类 + 中外合作办学普通专业` 计划：总计划 `18`、专业行 `4` 条，备注为“与英国思克莱德大学合作”；
       - `2025` 广西 `物理类 + 中外合作办学普通专业` 分数：最低分 `514`、最低位次 `45576`、平均分 `540.39`、最高分 `574`、专业行 `4` 条；
       - `2025` 广西 `少数民族预科` 分数：`物理类` 最低分 `558`、平均分 `564.4`、最高分 `570`；`历史类` 最低分 `571`、平均分 `572.8`、最高分 `576`；
       - `2024` 广西 `少数民族预科` 分数：`物理类` 录取人数 `5`、最低分 `564`、最低位次 `19064`；`历史类` 录取人数 `5`、最低分 `574`、最低位次 `3264`；
       - `2023` 广西 `少数民族预科` 分数：`理工` 录取人数 `5`、最低分 `492`、最低位次 `39052`；`文史` 录取人数 `5`、最低分 `578`、最低位次 `3186`；
       - `2022` 广西 `少数民族预科` 分数：`理工` 录取人数 `5`、最低分 `529`、最低位次 `20934`；`文史` 录取人数 `5`、最低分 `541`、最低位次 `8637`。
    2. 对应 bundle、分年 JSON、行级 CSV 与跨年汇总 CSV 已缓存到：
       - `raw_data/official_followup/yunnan_daxue_211/ynu_20250518_parallel_bundle.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_wuli_zhongwaihezuo_plan.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_wuli_zhongwaihezuo_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_wuli_zhongwaihezuo_score.json`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2025_guangxi_wuli_zhongwaihezuo_score_rows.csv`
       - 各 `ynu_20xx_guangxi_*_shaoshuminzuyuke_score.json` / `_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2025_guangxi_shaoshuminzuyuke_score_rows.csv`
  - 价值：
    1. 这把云南大学广西学校侧 API 线从“普通本科批 + 高校专项”继续扩展成“普通本科批 + 高校专项 + 中外合作办学普通专业 + 少数民族预科”四条并行子线。
    2. 其中 `中外合作办学普通专业` 首次把云南大学广西学校侧数据从普通批主线推进到项目型普通专业，`少数民族预科` 则补出一条连续 `2022-2025` 的广西分数时间线。

- 新增补齐一组 **云南大学学校侧广西 `艺术类 + 体育类` 连续四年并行时间线**：
  - 主入口仍为：
    - `https://zsfz.ynu.edu.cn/zsw/zsjh.html`
    - `https://zsfz.ynu.edu.cn/zsw/lnfs.html`
  - `2026-05-18` 服务器侧新增验证：
    1. 沿完全相同的 live `csrf(n=3) + X-Requested-Time + response-header Csrf-Token` 真链继续回放参数图里已公开的广西艺体组合后，成功一次性补齐：
       - `2025-2022` 四年连续的广西 `艺术类` 招生计划与录取分数；
       - `2025-2022` 四年连续的广西 `体育类` 招生计划与录取分数。
    2. 计划侧连续命中结果非常稳定：
       - `艺术类`：`2025/2024/2023/2022` 各年总计划都为 `6`，各年专业行都为 `1` 条，备注均显示“归属昌新国际艺术学院”；
       - `体育类`：`2025/2024/2023/2022` 各年总计划都为 `2`，各年专业行都为 `1` 条。
    3. 分数侧虽然没有 `zsSsgradeList` 学校级汇总行，但 `sszygradeList` 行级记录四年连续稳定返回，可直接形成专业级时间线：
       - `艺术类`：`2025` 最低分 `544`、`2024` 最低分 `544`、`2023` 最低分 `563`、`2022` 最低分 `592`；
       - `体育类`：`2025` 最低分 `540`、`2024` 最低分 `543`、`2023` 最低分 `530`、`2022` 最低分 `507`。
    4. 对应 bundle、分年 JSON、行级 CSV 与跨年汇总 CSV 已缓存到：
       - `raw_data/official_followup/yunnan_daxue_211/ynu_20250518_yiti_bundle.json`
       - 各 `ynu_20xx_guangxi_yishu_*.json` / `_rows.csv`
       - 各 `ynu_20xx_guangxi_tiyu_*.json` / `_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2025_guangxi_yishu_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2025_guangxi_yishu_score_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2025_guangxi_tiyu_plan_rows.csv`
       - `raw_data/official_followup/yunnan_daxue_211/ynu_2022_2025_guangxi_tiyu_score_rows.csv`
  - 价值：
    1. 这把云南大学广西学校侧 API 线从原来的四条子线，进一步扩展成“普通本科批 + 高校专项 + 中外合作办学普通专业 + 少数民族预科 + 艺术类 + 体育类”六条并行子线。
    2. 其中艺体分数侧虽然只有专业级记录，但连续四年都可直接返回，足以作为后续广西特殊类型时间序列的学校侧强基线。

- 新增补齐一个 **云南大学学校侧普通本科章程时间线**：
  - 学校侧招生政策栏目：`http://zsb.ynu.edu.cn/zszc.htm`
  - `2026-05-17` 服务器侧新增验证：
    1. `招生政策` 栏目及其分页可稳定访问；
    2. 沿分页继续下钻并逐页单独复核正文日期后，已确认以下普通本科招生章程正式页：
       - `http://zsb.ynu.edu.cn/info/1049/3163.htm` 《云南大学2025年本科招生章程》，页面发布时间 `2025-05-28`
       - `http://zsb.ynu.edu.cn/info/1049/2996.htm` 《云南大学2024年本科招生章程》，页面发布时间 `2024-05-21`
       - `http://zsb.ynu.edu.cn/info/1049/2763.htm` 《云南大学2023年本科招生章程》，页面发布时间 `2023-06-07`
       - `http://zsb.ynu.edu.cn/info/1049/2461.htm` 《云南大学2022年本科招生章程》，页面发布时间 `2022-05-19`
       - `http://zsb.ynu.edu.cn/info/1049/2129.htm` 《云南大学2021年本科招生章程》，页面发布时间 `2021-05-31`
       - `http://zsb.ynu.edu.cn/info/1049/1783.htm` 《云南大学2020年本科招生章程》，页面发布时间 `2020-06-22`
       - `http://zsb.ynu.edu.cn/info/1049/1644.htm` 《云南大学2019年本科招生章程》，页面发布时间 `2019-05-29`
    3. 同轮继续回看 `http://zsb.ynu.edu.cn/zszc/9.htm` 的列表上下文与对应正文页后，又确认了两条更早年度的普通本科章程页：
       - `http://zsb.ynu.edu.cn/info/1049/1108.htm` 《云南大学2018年本科招生章程》，当前学校站点可见发布时间 `2018-12-06`
       - `http://zsb.ynu.edu.cn/info/1049/1123.htm` 《云南大学2017年本科招生章程》，当前学校站点可见发布时间 `2018-08-18`
       这两条旧页的可见时间都晚于章程标题年份，更像学校站点保留/迁移后的现存发布时间展示，因此可以作为更早年度的官方基线继续保留，但在后续比对时要把它们和 `2019-2025` 那组“标题年份与可见发布时间更自然一致”的条目区别看待。
    4. 同轮继续回看 `http://zsb.ynu.edu.cn/zszc.htm` 首页的特殊类型条目后，又确认了两条学校侧 `2026` 特殊类型招生简章：
       - `http://zsb.ynu.edu.cn/info/1049/3328.htm` 《云南大学2026年依据台湾地区大学入学考试学科能力测试成绩招收台湾高中毕业生招生简章》，页面发布时间 `2025-12-12`
       - `http://zsb.ynu.edu.cn/info/1049/3319.htm` 《云南大学2026年招收香港中学文凭考试学生招生简章》，页面发布时间 `2025-12-04`
       这说明云南大学学校侧 `招生政策` 栏并不只是普通本科章程时间线，也已经形成了面向 `2026` 的台湾地区与香港中学文凭考试特殊类型正式发布链。
    5. 同轮继续回看同一首页的项目型条目后，又确认了两条学校侧 `2025` 项目型招生简章：
       - `http://zsb.ynu.edu.cn/info/1049/3189.htm` 《云南大学云南马来亚学院2025年招生简章》，页面发布时间 `2025-06-09`
       - `http://zsb.ynu.edu.cn/info/1049/3164.htm` 《云南大学2025年大气科学专业定向培养招生简章》，页面发布时间 `2025-06-06`
       这说明云南大学学校侧 `招生政策` 栏还承担着项目型招生发布功能，并不只是普通本科章程与港澳台特殊类型栏目的汇总入口。
  - 价值：
    1. 这把云南大学从“只有 query shell 入口已确认、接口仍阻塞”的状态推进到“学校侧 `2017-2025` 普通本科章程时间线也已明确”的更完整状态。
    2. 即使短期内 `招生计划 / 往年招生 / 录取信息查询` 接口仍旧阻塞，项目也已经具备云南大学学校侧稳定的普通本科规则基线与 `2026` 特殊类型发布链。
    3. 这也说明 `招生政策` 栏本身就值得继续低成本回看，不只是拿来补普通本科章程，还能稳定产出港澳台和项目型正式页。
    4. 后续再继续补抓时，优先顺着 query shell 的真实接口重写层和参数约束深挖，而不是重复做低价值的入口确认。

- 新增澄清一个 **中国石油大学（华东）学校侧直达入口 timeout 口径**：
  - 学校主站入口：[中国石油大学（华东）本科招生网](https://zhaosheng.upc.edu.cn/)
  - 主页已暴露的两条学校侧直达入口：
    - `https://zhaosheng.upc.edu.cn/cms/frontList.html?id=3500ec89203e47628ebe7d0370180828`
    - `https://zhaosheng.upc.edu.cn/static/front/upc/basic/html_cms/frontXylist.html?id=d04b496a3d9545c28ec2734126d3505f`
  - `2026-05-17` 服务器侧新增验证：
    1. 先从学校本科招生主页复核两条直达入口 URL；
    2. 再用服务器侧 `curl` 以浏览器 `User-Agent` 直探这两条入口；
    3. 两条请求都在 `15` 秒内 `0` 字节超时，返回 `HTTP 000`，错误均为 `Operation timed out after 15002 milliseconds with 0 bytes received`。
  - 价值：
    1. 这把中国石油大学（华东）从“只有主页缓存、仍待发现有效页面”推进到“学校侧两条低成本直达入口已确认 timeout 阻塞”。
    2. 后续不再继续盲打这两条同页，优先等待服务器链路变化，或改从学校主站其他带日期正文页补新的正式锚点。

- 新增打通一条 **中国石油大学（华东）学校侧招生政策 API 章程链**：
  - 学校主站入口：[中国石油大学（华东）本科招生网](https://zhaosheng.upc.edu.cn/)
  - `2026-05-17` 服务器侧新增验证：
    1. 先从主页缓存确认前端 `newAjax` 实际请求的是 `$.url('f/newsCenter/ajax_category_article_list')`，再从 `init.js` 读到 `招生政策` 栏目 `categoryId=c9d787239b4847c3b2a48b9780bb1772`；
    2. 再从 `tplt.js` 确认该站点并不是直接裸打文章接口，而是先调用 `/f/ajax_get_csrfToken` 取得 `Csrf-Token`，然后带 token 回放 `/f/newsCenter/ajax_category_article_list`；
    3. 继续用服务器侧 `requests.Session` 按“主页暖会话 -> csrf -> article list”的最小链路回放后，`/f/ajax_get_csrfToken` 返回 `200`，且 `招生政策` 栏目文章接口同样返回 `200` 官方 JSON；
    4. 该官方 JSON 直接返回 `2025 / 2024 / 2023 / 2022 / 2021` 五条本科招生章程，标题与发布时间分别为：
       - `中国石油大学（华东）2025年本科招生章程` `2025-05-22 17:16:00`
       - `中国石油大学（华东）2024年本科招生章程` `2024-05-24 20:17:00`
       - `中国石油大学（华东）2023年本科招生章程` `2023-06-01 19:26:00`
       - `中国石油大学（华东）2022年本科招生章程` `2022-05-21 20:50:00`
       - `中国石油大学（华东）2021年招生章程` `2021-06-08 16:49:00`
    5. 实时返回已缓存为 `raw_data/official_followup/zhongguo_shiyou_huadong_211/zszc_category_list_20260517.json`。
  - 价值：
    1. 这把中国石油大学（华东）从“主页存在、两条直达页 timeout”推进到“学校侧招生政策 API 已打通，并已确认连续 `2021-2025` 本科招生章程链”。
    2. 也就是说，这条线不再只是一个网络阻塞案例，而是已经补出一组可直接落表的正式官方章程基线。
    3. 后续继续补抓时，应优先沿同一套 `csrf + newsCenter` 机制去扩招生动态、特殊类型或项目型正式页，而不是再优先撞那两条 `frontList/frontXylist` 超时入口。

- 新增打通一条 **中国石油大学（华东）学校侧特殊类型发布链**：
  - 学校主站入口：[中国石油大学（华东）本科招生网](https://zhaosheng.upc.edu.cn/)
  - `2026-05-17` 服务器侧新增验证：
    1. 继续沿已打通的 `csrf + newsCenter/ajax_category_article_list` 机制下钻，并先通过 `f/newsCenter/ajax_shelf_and_child_category_list` 命中 `特殊类型招生` 栏目 `categoryId=642bd32edac641f8915ff3b4b3a70267`；
    2. 该官方返回并非空壳，而是直接列出六个学校侧子栏：
       - `综合评价招生` `3500ec89203e47628ebe7d0370180828`
       - `高校专项计划` `c37359bdf39d493ea917bfc9eea1f7c1`
       - `艺术类` `b1cb2abba05f4448ba244bcc5d1d1b48`
       - `运动训练` `d7afac8e13b5407ab8919cd29f68adf5`
       - `港澳台招生` `179a2af70ec64f6b973ed6c1a13085a6`
       - `保送生` `27da4cb708b443f389f6f7a240ff2726`
    3. 再用同一套 token 回放链分别下钻这些子栏后，已直接确认一组带日期的代表性正式简章：
       - `中国石油大学（华东）2026年综合评价招生简章` `2026-04-24 15:46:00`
       - `中国石油大学（华东）2025年高校专项计划招生简章` `2025-04-01 17:35:00`
       - `中国石油大学（华东）2025年音乐学专业招生简章` `2025-05-30 17:07:00`
       - `中国石油大学（华东）2026年运动训练专业招生简章` `2026-01-23 18:39:00`
       - `中国石油大学（华东）2026年招收台湾地区高中毕业生简章` `2025-12-10 14:33:00`
       - `中国石油大学（华东）2026年保送生招生简章` `2026-02-03 09:45:00`
    4. 六个特殊类型子栏的实时返回已整体缓存为 `raw_data/official_followup/zhongguo_shiyou_huadong_211/special_type_lists_20260517.json`。
  - 价值：
    1. 这把中国石油大学（华东）从“只补出普通本科章程”进一步推进到“学校侧特殊类型发布链也已打通”的状态。
    2. 也就是说，这条线现在已经同时具备 `普通本科章程时间线` 与 `六个特殊类型子栏` 两层官方证据链。
    3. 后续如果继续补抓，优先顺着同一套 `csrf + newsCenter` 机制去扩综合评价、港澳台或保送生的更早年份与流程通知，而不是回到那两条超时直达页。

- 新增澄清一个 **中国矿业大学招生壳页存活但主站常见入口失效的口径**：
  - 学校侧招生计划壳页：`http://zs.cumt.edu.cn/zsw/zsjh.html`
  - `2026-05-17` 服务器侧新增验证：
    1. 先直探常见主站路径 `https://www.cumt.edu.cn/zsjy.htm`，返回 `404错误提示` 页面；
    2. 早先缓存里保留下来的学校侧招生计划壳页 `http://zs.cumt.edu.cn/zsw/zsjh.html` 的确能看到 `f/ajax_zsjh_param`、`f/ajax_zsjh`、`f/ajax_zyjs_zy` 三组接口路径；
    3. 但同日后续再做低成本服务器复核时，无论默认请求头还是浏览器 `User-Agent`，`http://zs.cumt.edu.cn/zsw/zsjh.html` 本身、静态 JS `http://zs.cumt.edu.cn/static/front/cumt/basic/js/init.js` 与 `tplt.js`，以及 `http://zs.cumt.edu.cn/f/ajax_get_csrfToken` 和 `f/ajax_zsjh_param` 都统一直返 `HTTP 403`。
  - 价值：
    1. 这把中国矿业大学从“只有静态壳页缓存、主站口径不清”推进到更收紧的“主站常见入口失效，且学校侧壳页 / 静态资源 / csrf / 参数接口整族统一 403”的阻塞状态。
    2. 后续如果继续补抓，不应再按“壳页活着、只差接口 replay”的旧假设重复试探，而应优先等待链路条件变化、会话来源变化，或改找学校主站其他带日期正文页作为新的本科锚点。

- 新增把 **中国石油大学（北京）** 从“`http -> https` 升级后参数接口阻塞”继续收紧为“真实 `csrf` 入口本身就被挡住”的口径：
  - 学校主站入口：[本科招生](https://www.cup.edu.cn/dbewm/8cd0dc4a2eec46129adf843b29b6571f.htm)
  - 学校主页与旧壳页：
    - `https://bkzs.cup.edu.cn/f`
    - `http://bkzs.cup.edu.cn/static/front/cup/basic/html/web/zsjh.html`
    - `http://bkzs.cup.edu.cn/static/front/cup/basic/html/web/lnfs.html`
  - `2026-05-17` 服务器侧先完成过一轮旧口径复核：
    1. 先暖主页 `http://bkzs.cup.edu.cn/f` 获取会话 cookie；
    2. 再带 `Referer`、`Origin`、`X-Requested-With` 回放 `http://bkzs.cup.edu.cn/f/ajax_zsjh_param`；
    3. 该 `http` 接口并非直接返回 `403`，而是先 `302` 跳到 `https://bkzs.cup.edu.cn/f/ajax_zsjh_param`；
    4. 继续切到 `https` 并携带主页 cookie 与同域请求头后，`ajax_zsjh_param` 与 `ajax_lnfs_param` 都统一返回 `403`。
  - `2026-05-18` 服务器侧又沿 live `tplt.js` 把真实链路补死：
    1. 直接抓取 `https://bkzs.cup.edu.cn/static/front/cup/basic/js/tplt.js` 后，已确认页面真实顺序是 `POST f/ajax_get_csrfToken (n=3)`，再把返回 token 串拆分后轮转写入 `Csrf-Token` 请求头提交 `f/ajax_zsjh_param` / `f/ajax_lnfs_param`；
    2. 再用 `https://bkzs.cup.edu.cn/f` 暖会话后，确实能拿到 `zhaosheng.cup.session.id`；
    3. 但即便带主页会话与同域 `Referer`、`Origin`、`X-Requested-With` 回放 `https://bkzs.cup.edu.cn/f/ajax_get_csrfToken`，接口本身仍直接返回 `403` 与 `{"state":0,"msg":"禁止访问"}`；
    4. 同轮再复核旧静态壳页 `https://bkzs.cup.edu.cn/static/front/cup/basic/html/web/zsjh.html` 与 `lnfs.html`，两页也都直返 `404`。
  - 价值：
    1. 这说明中国石油大学（北京）不是“只差补齐 `csrf` 逻辑”的轻阻塞，而是“主页存活但真实 token 入口即 `403`，旧静态壳页同时 `404`”的更硬门禁。
    2. 后续不再按老的 `http` 直打口径或错壳页口径重复消耗探针，而应优先等待会话来源变化或改找学校主站新的带日期本科正文页。

- 新增澄清一个 **北京科技大学 HTTPS 参数接口在会话回放后仍统一阻塞的口径**：
  - 学校侧招生壳页：
    - `https://zhaoshengyunzhi.ustb.edu.cn/zsw/zsjh.html`
    - `https://zhaoshengyunzhi.ustb.edu.cn/zsw/lnfs.html`
  - `2026-05-17` 服务器侧新增验证：
    1. 分别先暖 `zsjh.html` 与 `lnfs.html` 主页会话，获取站点 cookie；
    2. 再带 `Referer`、`Origin`、`X-Requested-With` 回放 `https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh_param` 与 `https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs_param`；
    3. 两个 HTTPS 参数接口都统一返回 `403`。
  - 价值：
    1. 这把北京科技大学从泛化的“接口层仍为 403”推进到“已经做过主页会话和同域请求头回放、接口依然统一阻塞”的更精确状态。
    2. 后续除非更换会话来源或网络出口，否则不再继续按同一套低成本回放方式重复试探。

- 新增澄清一个 **大连海事大学静态入口已从网络不通收紧为 404 的口径**：
  - 学校侧静态入口：
    - `https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html/web/zsjh.html`
    - `https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html/web/lnfs.html`
  - `2026-05-17` 服务器侧新增验证：
    1. 分别直探招生计划与历年分数静态入口；
    2. 两条入口都返回 `HTTP 404`；
    3. 远端地址均为 `202.118.86.37`。
  - 价值：
    1. 这把大连海事大学从早先粗粒度的“服务器到目标站点链路不通”收紧为“同家族静态入口当前直接 404”。
    2. 后续如果继续补抓，优先检查学校是否已更换入口路径或迁移到新的查询前端，而不是继续按单纯网络阻塞处理。
    3. 同轮继续检查官方 2025 计划发布正文内脚本暴露的 `https://zq-open.dlmu.edu.cn/` 备用域，发现其拼接路径更像站内搜索前端 `views/search/modules/resultpc/soso.html` 而不是招生查询系统本体；服务器侧直探该备用域根路径及其拼接后的 `zsjh.html` 也都在 `12` 秒内 `HTTP 000` 超时，因此暂不把它记作新的可用招生入口。

- 新增补齐一个 **石河子大学学校侧招生 / 查询入口链**：
  - 学校侧招生网首页：[石河子大学招生网](https://zsb.shzu.edu.cn/)
  - 本轮确认的学校侧入口：
    - 招生计划：`http://zsb.shzu.edu.cn/14096/list.htm`
    - 历年分数：`http://202.201.164.73/release-page/overyears?key=7d84af99e64a5d516ef68fd2`
    - 录取查询：`http://202.201.164.73/release-page/enroll?key=72600da979256eb4b50980b0`
    - 录取进程：`https://zsbxcx.shzu.edu.cn/lqjc`
  - `2026-05-17` 服务器侧新增验证：
    1. `https://zsb.shzu.edu.cn/` 可稳定访问，首页新闻区直接可见带日期的 [石河子大学2025年招生简章](https://zsb.shzu.edu.cn/2025/0703/c14104a226567/page.htm)；
    2. 该正式文章页标题为 `石河子大学2025年招生简章`，页面发布时间为 `2025-07-03`；
    3. 同轮继续直探学校侧 `招生计划 / 历年分数 / 录取查询 / 录取进程` 四条入口，四条入口都返回 `HTTP 200`；
    4. 其中 `http://zsb.shzu.edu.cn/14096/list.htm` 当前更像招生栏目壳页，尚未直接拆出带日期的计划正文列表；`202.201.164.73/release-page/*` 与 `zsbxcx.shzu.edu.cn/*` 两组查询页则已确认是活入口；
    5. 继续下钻 `http://202.201.164.73/release-page/overyears?key=7d84af99e64a5d516ef68fd2` 主脚本后，已确认脚本资源为 `/zjzwzhaolu/static/js/2025_11_12_19_44.4ea5c508a6566e762405.main.js`，前端配置中同时暴露第三方高考查询 API 基址 `https://api.zjzw.cn/zhaolu/api`（变量 `gkapi`）与相对路径基址 `ro=/goapi`；
    6. 同一脚本的 route registry 还直接出现了 `provinceConfig / provinceInfo / provinceList / provinceColTrend / provinceExport / scoreGetProvince / scoreLists / scoreLineTrend / volunteerConfig / volunteerEnrollInfo / volunteerLists` 等命名；
    7. 继续沿脚本注册表下钻后，已确认这些命名不是空壳，而是直接映射到具体路径：`/school/appschool/province/config|info|lists|colTrend|export`、`/school/appschool/score/getProvince|lists|colTrend`、`/school/appschool/volunteer/config|enrollInfo|lists`；
    8. 再用服务器侧最小方法探针验证时，`http://202.201.164.73/goapi/school/appschool/province/config`、`/score/getProvince`、`/volunteer/config` 三条代表路径直接 GET 都会回落到前端 HTML 壳页，而携带 `X-Requested-With`、`Origin`、`Referer` 的空 JSON POST 则统一返回 `405 Not Allowed`。
    9. 同轮继续下钻学校侧招生计划页 `http://zsb.shzu.edu.cn/14096/list.htm` 后，发现其前端脚本 `http://zsb.shzu.edu.cn/_upload/tpl/04/66/1126/template1126/zhaoshengjihua.js` 并非空壳，而是直接内嵌 `2025` 年招生计划的 `filterList` 与全量 `dataList`；其中 `filterList` 明确包含 `广西`，进一步本地解析 `dataList` 后确认广西共有 `36` 条 `本科普通批` 分专业计划，科类覆盖 `历史类` 与 `物理类`，且已抽取缓存为 `raw_data/official_followup/shihezi_daxue_211/shzu_2025_guangxi_plan_rows.csv`。
  - 价值：
    1. 这把石河子大学从“本地缓存里只有一段完整招生章程正文、但缺少稳定日期和学校侧入口链”推进到“已有带精确日期的学校侧招生简章页 + 四条活查询入口”的更具体状态。
    2. 进一步说，这条线已经不再只是“有活入口”，而是已经确认存在 `gkapi` / `ro=/goapi` 双层前端配置，以及一整组已经落到具体路径的省份、分数线、志愿分析接口簇。
    3. 这也把阻塞状态从粗粒度的“接口未知”推进到更精确的“路径已知、GET 壳页回退、简单 POST 405 的方法层阻塞”。
    4. 更关键的是，这条线已经不再只有“入口链 + API 家族暴露”，而是直接拿到了学校侧 `2025` 广西招生计划的静态前端数据源，能够在不依赖 `goapi` 方法层解锁的前提下先行落地 Guangxi 行级计划数据。
    5. 后续继续补抓时，应一边保留 `202.201.164.73/release-page/*` 暴露出的 `ro=/goapi` 与已知 `/school/appschool/...` 路径作为方法与参数拆解线，一边把 `zhaoshengjihua.js` 这条已经实锤的静态计划源作为当前优先使用的广西计划抓取基线。
    6. `2026-05-18` 又把 `release-page/overyears` 引用的主脚本正式缓存为 `raw_data/official_followup/shihezi_daxue_211/shzu_overyears_main_20251112.js`，并按脚本里真实的公开页加密逻辑做了一次更硬的最小探针：
       - 公开页路径命中 `/release-page/overyears`，会走 `needEncrypt=true` 分支，且匿名场景会把 `userName=""`、`token="null"` 代入 AES-CBC 封装；
       - 本轮已按该逻辑构造 `{data:<AES({})>,lock:"1"}` 请求体，并补齐 `X-TC-Timestamp` 请求头，再回放到 `http://202.201.164.73/goapi/school/appschool/province/config`；
       - 结果仍然直返 `HTTP 405 Not Allowed`，且完整响应头/响应体已存证到 `raw_data/official_followup/shihezi_daxue_211/shzu_goapi_encrypted_probe_province_config_20260518.txt`。
    7. 同轮再换测脚本里直接暴露的外部基址 `gkapi=https://api.zjzw.cn/zhaolu/api`，把完全相同的真加密请求切到 `https://api.zjzw.cn/zhaolu/api/school/appschool/province/config` 后，服务器侧已不再返回 `405`，而是直返 `HTTP 503 Service Temporarily Unavailable`，完整响应已存证到 `raw_data/official_followup/shihezi_daxue_211/shzu_gkapi_encrypted_probe_province_config_20260518.txt`。
  - 价值：
    1. 这把石河子的阻塞口径从“简单 XHR 空 POST 仍 405”进一步收紧成“连前端真实 AES 封装 + `X-TC-Timestamp` 的最小业务请求也仍 405”，说明本地 `/goapi` 这层并非只差一个普通请求头或空参数。
    2. 同时也把另一条外部 `gkapi` 线路的状态坐实成“当前可达但服务侧 `503`”，说明问题不只是同源网关，而是石河子这组公开查询接口在内外两层都存在更硬的服务阻塞。
    3. 后续在石河子这条线继续低成本推进时，应优先转向两类新角度：
       - 继续从页面组件里找真正的业务字段组合，再试 `gkapi=https://api.zjzw.cn/zhaolu/api` 外部基址；
       - 保留 `zhaoshengjihua.js` 这条已经稳定落地的广西计划静态源，避免再重复本地 `/goapi` 的空探针。

- 新增打通一个 **北京科技大学学校侧 2025 广西招生计划 API 官方数据源**：
  - 学校侧计划页：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/zsjh.html`
  - 计划接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh`
  - `2026-05-17` 服务器侧新增验证：
    1. 继续下钻北科大线上 `tplt.js` 后，确认它不是简单依赖 cookie，而是先同步 `POST /f/ajax_get_csrfToken` 且提交 `n=3`，随后把返回 `data` 里的 token 串拆分后写入后续请求头 `Csrf-Token`；
    2. 按这一真实顺序回放后，`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh_param` 成功返回 `200`，且响应头继续回写新的 `Csrf-Token`；
    3. 再用同链路回放 `https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh`，已直接返回 `2025` 年 `广西` `普通类` 招生计划；
    4. 其中 `物理类` 汇总 `zsjhTotal` 为 `66`，`历史类` 汇总 `zsjhTotal` 为 `6`，两类合计行级专业数据 `19` 条；
    5. 实时返回已缓存到：
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_zsjh_param.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_wuli_plan.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_lishi_plan.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_plan_rows.csv`
  - 价值：
    1. 这把北京科技大学从“学校侧同族接口经 cookie/Referer 回放后仍 403”的旧口径，推进到“按真实 `csrf + token chain` 顺序回放后，计划接口已打通”的新状态。
    2. 这条线也已经不只是“计划页存在”，而是直接拿到了学校侧 `2025` 广西 `本科普通批` 行级计划数据，可作为后续 Guangxi 志愿分析的直接官方源。
    3. 下一步更值得继续的是沿同一 token 链补历年分数接口，而不是再把北科大重复归类为泛化的 `403` 阻塞项。

- 新增打通一个 **北京科技大学学校侧 2025 广西录取分数 API 官方数据源**：
  - 学校侧分数页：`https://zhaoshengyunzhi.ustb.edu.cn/zsw/lnfs.html`
  - 分数接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs`
  - `2026-05-17` 服务器侧新增验证：
    1. 沿北科大 `历年分数` 页使用与 `招生计划` 同一条真实 token 链：先 `POST /f/ajax_get_csrfToken (n=3)`，再把 token 串拆分后写入 `Csrf-Token` 请求头回放 `https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs_param`；
    2. 参数接口成功返回 `200`，其中广西可用组合明确包括 `2025 物理类 普通类`、`2025 物理类 国家专项`、`2025 历史类 普通类`，并向前延伸到 `2024` 与 `2023/2022` 的广西组合；
    3. 再回放 `https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs` 后，已直接返回 `2025` 年广西普通类录取分数数据；
    4. 其中 `物理类` 省级汇总行显示：省控线 `495`、最低分 `603`、最低位次 `5738`、平均分 `608.72`、最高分 `622`，专业行 `16` 条；
    5. `历史类` 省级汇总行显示：省控线 `518`、最低分 `596`、最低位次 `1557`、平均分 `597.17`、最高分 `599`，专业行 `3` 条；
    6. 实时返回已缓存到：
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_lnfs_param.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_wuli_score.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_lishi_score.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_score_rows.csv`
  - 价值：
    1. 这把北京科技大学从“计划 API 已通”继续推进到“计划 + 分数 API 同链路都已打通”的更强状态。
    2. 当前北科大已经不再只是有 dated regulation baseline，而是已经具备可直接用于广西物理/历史普通类比较的学校侧计划与录取分数双源。
    3. 后续沿同一 token 链继续补 `国家专项` 或前几年广西分数，性价比会明显高于再回头试探旧 403 口径。

- 新增补齐一条 **北京科技大学学校侧 2025 广西物理类国家专项录取分数源**：
  - 分数接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs`
  - `2026-05-17` 服务器侧新增验证：
    1. 沿北科大 `历年分数` 页已打通的 token 链，继续回放 `ssmc=广西`、`zsnf=2025`、`klmc=物理类`、`zslx=国家专项`；
    2. 官方接口成功直接返回国家专项汇总与专业行数据；
    3. 汇总行显示：录取人数 `8`、省控线 `495`、最低分 `546`、最低位次 `27014`、平均分 `556.38`、平均位次 `22022`、最高分 `569`、最高位次 `16339`；
    4. 专业行共 `3` 条，当前已确认包括：
       - `土木类（未来城市建设、诊治与运维）`
       - `矿业类`
       - `冶金工程（低碳智慧冶金和战略金属提取）`
    5. 实时返回已缓存到：
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_wuli_national_special_score.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2025_guangxi_wuli_national_special_score_rows.csv`
  - 价值：
    1. 这把北科大从“广西普通类计划 + 分数已打通”进一步推进到“广西国家专项分数也已落地”的更细粒度状态。
    2. 当前北科大学校侧广西来源已经同时覆盖 `普通类` 与 `国家专项` 两类分数线索，后续扩展专项计划或回推上年专项分数都有了明确低成本入口。

- 新增补齐两条 **北京科技大学学校侧 2024 广西连续基线**：
  - 计划接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh`
  - 分数接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs`
  - `2026-05-17` 服务器侧新增验证：
    1. 沿北科大已打通的同一 token 链，继续回放 `广西 + 2024 + 物理类/历史类 + 普通类`；
    2. 计划侧成功直接返回 `2024` 年广西 `本科普通批` 招生计划：
       - `物理类` 总计划数 `65`、专业行 `17` 条；
       - `历史类` 总计划数 `6`、专业行 `3` 条；
       - 合并行级计划 `20` 条。
    3. 分数侧成功直接返回 `2024` 年广西普通类专业行分数：
       - `物理类` 专业行 `17` 条；
       - `历史类` 专业行 `3` 条；
       - 合并专业行 `20` 条；
       - 该年接口当前未单独给出 `zsSsgradeList` 省级汇总行，但专业行字段完整，足够直接作为 Guangxi 行级分数基线。
    4. 实时返回已缓存到：
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_wuli_plan.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_lishi_plan.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_plan_rows.csv`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_wuli_score.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_lishi_score.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_score_rows.csv`
  - 价值：
    1. 这把北京科技大学从“只有 `2025` Guangxi 计划/分数已打通”推进到“`2024-2025` 连续学校侧 Guangxi baseline”。
    2. 现在北科大不仅有连续章程基线，也已有连续两年的广西计划与录取分数接口证据链，更适合后续做 `2026` 对照和异常波动核查。

- 新增继续向前补齐一组 **北京科技大学学校侧 2023/2022 广西理工基线**：
  - 计划接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh`
  - 分数接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs`
  - `2026-05-17` 服务器侧新增验证：
    1. 参数页已明确公开 `广西_2023_理工_普通类`（计划）以及 `广西_2023_理工_普通类/国家专项`、`广西_2022_理工_普通类`（分数）组合；
    2. 继续沿同一 token 链回放后，已成功拿到：
       - `2023` 广西理工普通类计划：总计划数 `67`、专业行 `16` 条；
       - `2023` 广西理工普通类分数：录取人数 `69`、最低分 `598`、最低位次 `5583`、平均分 `604.93`、最高分 `620`、专业行 `16` 条；
       - `2023` 广西理工国家专项分数：录取人数 `8`、最低分 `574`、最低位次 `9810`、平均分 `578.25`、最高分 `592`、专业行 `7` 条；
       - `2022` 广西理工普通类分数：录取人数 `67`、最低分 `577`、最低位次 `8005`、平均分 `592.45`、最高分 `615`、专业行 `14` 条。
    3. 实时返回已缓存到：
       - `raw_data/official_followup/beijing_keji_211/plan_2023_ligong_putong.json`
       - `raw_data/official_followup/beijing_keji_211/score_2023_ligong_putong.json`
       - `raw_data/official_followup/beijing_keji_211/score_2023_ligong_nspecial.json`
       - `raw_data/official_followup/beijing_keji_211/score_2022_ligong_putong.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2023_guangxi_plan_rows.csv`
       - `raw_data/official_followup/beijing_keji_211/ustb_2022_2023_guangxi_score_rows.csv`
  - 价值：
    1. 这把北京科技大学学校侧 Guangxi 证据链从 `2024-2025` 再往前推进到 `2023` 计划 + 分数，以及 `2022` 分数。
    2. 目前北科大已经形成了覆盖 `2022-2025` 的广西分数时间线，以及 `2023-2025` 的广西计划时间线，并兼有 `2025` 与 `2023` 的国家专项分数线索，足够作为后续 `2026` 变动对照的强基线。

- 新增把 **中国石油大学（华东）** 从“章程 + 特殊类型”继续扩成 **通知公告 / 招生动态链**：
  - 学校主站入口：[中国石油大学（华东）本科招生网](https://zhaosheng.upc.edu.cn/)
  - 栏目 JSON 缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_notice_dynamic_lists_20260518.json`
  - `2026-05-18` 服务器侧新增验证：
    1. 先从主页引用的 `init.js` 直接坐实首页栏目号：
       - `通知公告` `categoryId=3148a5449c78447ca7dd10a728994df9`
       - `招生动态` `categoryId=e8659322e16240d296178402510b34f2`
    2. 再沿同一套已打通的真链 `主页暖会话 -> POST /f/ajax_get_csrfToken(n=3) -> /f/newsCenter/ajax_category_article_list` 分别回放两栏；
    3. `通知公告` 官方 JSON 直接返回一组带日期的正式页，其中新增较有价值的包括：
       - `2025年招生专业信息一站通` `2025-04-30 14:03:00`
       - `2025年培养模式详解` `2025-07-01 15:42:00`
    4. `招生动态` 官方 JSON 也直接返回学校侧动态链，其中新增较有价值的一条是：
       - `生源质量持续攀升！学校2025年本科招生录取工作圆满收官` `2025-08-03 14:11:00`
       - 该条目在 JSON 中直接指向学校官方新闻网正文 `https://news.upc.edu.cn/info/1432/117349.htm`
  - 价值：
    1. 这把中国石油大学（华东）从原来的“学校侧章程链 + 特殊类型链”继续推进到“通知公告 / 招生动态”两条并行发布链也已打通。
    2. 也就是说，这条线现在已经不只是招生章程和专项简章，还补出了一组 `2025` 年度的专业信息服务、培养模式说明和录取收官动态正式页。
    3. 后续如果继续下钻，更适合沿同一套 `csrf + newsCenter` 机制去扩 `通知公告` / `招生动态` 的更早年份或更具体的计划、录取流程页，而不是再回到 `frontList/frontXylist` 那两条已知 timeout 的直达入口。

- 新增继续向前补齐两条 **中国石油大学（华东）学校侧通知 / 动态正式页**：
  - 学校主站入口：[中国石油大学（华东）本科招生网](https://zhaosheng.upc.edu.cn/)
  - 扩展后的两栏 JSON 缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_notice_dynamic_lists_full_20260518.json`
  - `2026-05-18` 服务器侧新增验证：
    1. 继续沿同一套真链 `主页暖会话 -> POST /f/ajax_get_csrfToken(n=3) -> /f/newsCenter/ajax_category_article_list`，把 `通知公告` 与 `招生动态` 两栏 `pageSize` 从 `10` 扩到 `50`；
    2. `招生动态` 栏又新增命中一条较有价值的往年正式页：
       - `学校顺利完成2024年本科招生录取工作` `2024-08-02 15:21:00`
       - 条目直接指向学校官方新闻网正文 `https://news.upc.edu.cn/info/1432/114656.htm`
    3. `通知公告` 栏又新增命中一条此前未入账的专项正式页：
       - `中国石油大学（华东）2026年保送录取优秀运动员招生简章` `2026-01-19 09:27:00`
       - 文章页路径为 `https://zhaosheng.upc.edu.cn/cms/frontViewArticle.html?id=f65c28787f334dfb8a83f9968f67bd77`
  - 价值：
    1. 这把中国石油大学（华东）学校侧 `录取收官动态` 从原来的 `2025` 单点往前补到 `2024-2025` 两年链。
    2. 也把学校侧 `保送生` 线从先前代表性的 `2026年保送生招生简章`，进一步补成更具体的 `2026年保送录取优秀运动员招生简章` 正式页。
    3. 现在这条线已经同时具备 `本科章程`、`六个特殊类型子栏`、`通知公告/招生动态` 以及 `录取收官动态` 的更完整并行证据链。

- 新增把 **中国石油大学（华东）特殊类型子栏** 继续补成一组近年时间线：
  - 六个子栏长列表缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 服务器侧新增验证：
    1. 继续沿同一套真链 `主页暖会话 -> POST /f/ajax_get_csrfToken(n=3) -> /f/newsCenter/ajax_category_article_list`，把 `综合评价招生 / 高校专项计划 / 艺术类 / 运动训练 / 港澳台招生 / 保送生` 六个子栏统一扩到 `20` 条长列表；
    2. 在原先只登记各子栏“代表性单条”基础上，又补出一组近期正式简章：
       - `中国石油大学（华东）2025年综合评价招生简章` `2025-04-29 16:42:00`
       - `中国石油大学（华东）2024年综合评价招生简章` `2024-04-23 15:00:00`
       - `中国石油大学（华东）2024年高校专项计划招生简章` `2024-04-04 12:25:00`
       - `中国石油大学（华东）2024年音乐学专业招生简章` `2024-05-28 09:47:00`
       - `中国石油大学（华东）2026年招收香港中学文凭考试学生简章` `2025-11-17 08:02:00`
       - `中国石油大学（华东）2026年中国普通高等学校联合招收澳门保送生简章` `2025-10-22 07:55:00`
       - `中国石油大学（华东）2025年招收台湾地区高中毕业生简章` `2024-12-09 15:39:00`
       - `中国石油大学（华东）2025年招收香港中学文凭考试学生简章` `2024-11-27 10:31:00`
       - `中国石油大学（华东）2025年中国普通高等学校联合招收澳门保送生简章` `2024-10-25 14:31:00`
       - `中国石油大学（华东）2025年保送生招生简章` `2025-01-10 14:44:00`
  - 价值：
    1. 这把中国石油大学（华东）原本偏“代表性样本”的特殊类型链，推进成一组更适合后续对照的近年时间线。
    2. 现在不仅有 `2026` 单年简章，还补齐了若干 `2025/2024` 上年基线，覆盖 `综合评价 / 高校专项 / 音乐学 / 港澳台 / 保送生` 多条并行子线。
    3. 后续如果继续下钻，优先顺着同一缓存去补这些子栏的 `2023/2022` 近前历史版本，而不是再重新试探阻塞入口。

- 新增继续把 **中国石油大学（华东）特殊类型近年基线** 再往前补厚一截：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从已落地的六子栏长列表里筛净新增正式简章，又补出：
       - `中国石油大学（华东）2023 / 2022 / 2021 年综合评价招生简章`
       - `中国石油大学（华东）2023 / 2022 / 2021 年高校专项计划招生简章`
       - `中国石油大学（华东）2023 / 2022 / 2021 年音乐学专业招生简章`
       - `中国石油大学（华东）2024 年招收台湾地区高中毕业生简章`
       - `中国石油大学（华东）2024 年招收香港中学文凭考试学生简章`
       - `中国石油大学（华东）2024 年中国普通高等学校联合招收澳门保送生简章`
    2. 这些页面发布时间分别落在 `2021-2024`，且都直接来自同一学校侧官方 JSON 子栏长列表。
  - 价值：
    1. 这一步把华东石油的 `综合评价 / 高校专项 / 音乐学` 三条特殊类型子线都明确往前补成了 `2021-2026` 量级的连续基线。
    2. `港澳台招生` 也从原来偏 `2025/2026` 的近年样本，补成了至少含 `2024-2026` 的更稳上年对照链。
    3. 现在华东石油这条学校侧文章服务线已经不只是“发现可用”，而是开始具备做后续年份比对的厚时间线价值。

- 新增继续把 **中国石油大学（华东）港澳台招生子线** 从 `2024-2026` 再往前补成连续长链：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一长列表里筛净新增正式简章，又补出：
       - `中国石油大学（华东）2023 年招收台湾地区高中毕业生简章`
       - `中国石油大学（华东）2023 年招收香港中学文凭考试学生简章`
       - `中国石油大学（华东）2023 年中国普通高等学校联合招收澳门保送生简章`
       - `中国石油大学（华东）2022 年招收台湾地区高中毕业生简章`
       - `中国石油大学（华东）2022 年招收香港中学文凭考试学生简章`
       - `中国石油大学（华东）2022 年中国普通高等学校联合招收澳门保送生简章`
       - `中国石油大学（华东）2021 年招收台湾地区高中毕业生简章`
       - `中国石油大学（华东）2021 年招收香港中学文凭考试学生简章`
       - `中国石油大学（华东）2021 年中国普通高等学校联合招收澳门保送生简章`
       - `中国石油大学（华东）2020 年招收台湾高中毕业生简章`
    2. 这些页面发布时间落在 `2020-2023`，且都直接来自学校侧官方 JSON 长列表，不需要再开新探路。
  - 价值：
    1. 这一步把华东石油的 `港澳台招生` 子线从原来的 `2024-2026` 进一步补成 `2020-2026` 连续基线。
    2. 华东石油这条学校侧文章服务线现在不仅有普通本科章程、通知公告、招生动态和多条特殊类型代表页，还开始具备更长跨度的港澳台对照能力。

- 新增继续把 **中国石油大学（华东）高校专项子线** 从 `2021-2025` 再往前补成长期连续链：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一 `高校专项计划` 子栏长列表里筛净新增正式简章，又补出：
       - `中国石油大学（华东）2020 年高校专项计划招生简章`
       - `中国石油大学（华东）2019 年高校专项计划招生简章`
       - `中国石油大学（华东）2018 年高校专项计划招生简章`
       - `中国石油大学（华东）2017 年高校专项计划招生简章`
       - `中国石油大学（华东）2016 年高校专项计划招生简章`
       - `2015 年农村专项自主招生简章`
       - `2014 年农村专项自主选拔录取招生简章`
    2. 这些页面发布时间落在 `2014-2020`，且都直接来自学校侧官方 JSON 长列表，不需要再开新探路。
  - 价值：
    1. 这一步把华东石油的 `高校专项` 子线从原来的 `2021-2025` 进一步补成 `2014-2025` 连续长基线。
    2. 配合已经补齐的 `港澳台 2020-2026` 子线，华东石油的学校侧特殊类型发布链已经开始具备真正的长跨度年份对照价值，而不只是近年代表样本。

- 新增继续把 **中国石油大学（华东）音乐学 / 高水平运动队子线** 也补成连续链：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一长列表里筛净新增正式简章，又补出：
       - `中国石油大学（华东）2020 年音乐学专业招生简章`
       - `中国石油大学（华东）2019 年音乐学专业招生简章`
       - `中国石油大学（华东）2023 年高水平运动队招生简章`
       - `中国石油大学（华东）2022 年高水平运动队招生简章`
       - `中国石油大学（华东）2021 年高水平运动队招生简章`
    2. 这些页面发布时间落在 `2019-2022`，且都直接来自学校侧官方 JSON 长列表，不需要再开新探路。
  - 价值：
    1. 这一步把华东石油的 `音乐学` 子线从原来的 `2021-2025` 进一步补成 `2019-2025` 连续基线。
    2. 也把 `运动训练 / 高水平运动队` 子线明确补成 `2021-2026` 连续基线。
    3. 到这里，华东石油学校侧特殊类型发布链已经形成多条可做长期年份对照的并行子线，而不只是零散代表页。

- 新增补齐一组 **中国石油大学（华东）综合评价 / 高校专项过程通知链**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净新增正式页，补出 `2025-2022` 连续四年的综合评价招生入选名单通知：
       - `关于公示中国石油大学（华东）2025年综合评价招生入选考生名单的通知` `2025-06-19 12:51:00`
       - `关于公示中国石油大学（华东）2024年综合评价招生入选考生名单的通知` `2024-06-20 21:26:00`
       - `关于公示中国石油大学（华东）2023年综合评价招生入选考生名单的通知` `2023-06-20 18:41:00`
       - `关于公示中国石油大学（华东）2022年综合评价招生入选考生名单的通知` `2022-06-23 11:38:00`
    2. 同轮再补出 `2025-2022` 连续四年的高校专项计划入选名单通知：
       - `关于公示中国石油大学（华东）2025年高校专项计划入选名单的通知` `2025-05-27 08:35:00`
       - `关于公示中国石油大学（华东）2024年高校专项计划入选名单的通知` `2024-05-28 18:54:00`
       - `关于公示中国石油大学（华东）2023年高校专项计划入选名单的通知` `2023-05-31 15:34:00`
       - `关于公示中国石油大学（华东）2022年高校专项计划入选名单的通知` `2022-05-31 11:46:00`
  - 价值：
    1. 这一步把华东石油从“有特殊类型简章时间线”继续推进到“连入选结果公告也有连续年份链”，后续更适合比较学校侧发布节奏与流程变化。
    2. 现在华东石油的综合评价与高校专项两条子线，都已经同时覆盖“简章 + 结果公告”两层结构，学校侧特殊类型证据链明显更厚。

- 新增继续把 **中国石油大学（华东）综合评价 / 高校专项过程通知链** 往前补长：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份官方长列表缓存里筛净新增正式页，补出 `2025/2023/2022/2021/2020` 五条综合评价招生初审结果通知：
       - `关于公示中国石油大学（华东）2025年综合评价招生初审结果的通知` `2025-06-04 19:47:00`
       - `关于公示中国石油大学（华东）2023年综合评价招生初审结果的通知` `2023-06-02 18:55:00`
       - `关于公示中国石油大学（华东）2022年综合评价招生初审结果的通知` `2022-06-02 15:27:00`
       - `关于公示中国石油大学（华东）2021年综合评价招生初审结果的通知` `2021-06-04 12:15:00`
       - `中国石油大学（华东）关于公示2020年综合评价招生初审结果的通知` `2020-07-06 13:19:00`
    2. 同轮再把高校专项计划入选名单子线继续往前补长，新增 `2021/2020/2019/2018` 四条正式通知：
       - `关于公示中国石油大学（华东）2021年高校专项计划入选名单的通知` `2021-05-28 19:41:00`
       - `中国石油大学（华东）关于公示2020年高校专项计划入选名单的通知` `2020-06-30 21:11:00`
       - `中国石油大学（华东）关于公示2019年高校专项计划入选名单的通知` `2019-05-29 15:32:00`
       - `中国石油大学（华东）关于公示2018年高校专项计划入选名单的通知` `2018-06-05 09:33:00`
  - 价值：
    1. 这一步把华东石油的综合评价子线进一步推进成“`2020-2025` 连续初审 / 入选结果公告并行”的更完整过程链。
    2. 也把高校专项过程通知子线从原来的 `2022-2025` 补长为 `2018-2025` 连续入选名单链，明显增强了学校侧长期流程对照能力。

- 新增补齐一条 **北京科技大学学校侧 2024 广西物理类国家专项分数源，并坐实计划下界**：
  - 分数接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs`
  - 计划接口：`https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_zsjh`
  - `2026-05-18` 服务器侧新增验证：
    1. 继续沿同一真实 token 链回放 `广西 + 2024 + 物理类 + 国家专项`，成功直接返回 `2024` 年广西物理类国家专项录取分数数据；
    2. 汇总行显示录取人数 `8`、省控线 `501`、最低分 `555`、最低位次 `23524`、平均分 `570.63`、最高分 `597`，并含 `4` 条专业行，样例包括 `土木类` `555-575 / 23524-15077` 与 `通信工程` `597 / 8239`；
    3. 同轮再沿招生计划链回放 `广西 + 2022 + 理工 + 普通类`，接口虽仍返回 `state=1` / `msg=操作成功`，但 `zsjhTotal=[]`、`zsjhList=[]`，说明这不是链路失效，而是学校侧当前不再公开这一年广西普通类计划；
    4. 实时返回已缓存到：
       - `raw_data/official_followup/beijing_keji_211/ustb_20240518_probe_bundle.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_wuli_national_special_score.json`
       - `raw_data/official_followup/beijing_keji_211/ustb_2024_guangxi_wuli_national_special_score_rows.csv`
  - 价值：
    1. 这把北京科技大学广西国家专项分数链从原来的 `2023`、`2025` 两个断点补成了 `2023-2025` 的连续三年序列。
    2. 也把北京科技大学广西计划时间线的学校侧公开下界正式收敛到 `2023-2025`，后续不必再按同一角度盲试 `2022` 广西理工普通类计划。
    3. 再结合已落地的 `ustb_2025_zsjh_param.json` 与 `ustb_2025_lnfs_param.json` 可进一步坐实：`zsjh_param` 当前只公开广西 `普通类` 计划组合（`2025/2024 物理类`、`2025/2024 历史类`、`2023 理工`），而 `lnfs_param` 还公开了 `2025/2024/2023` 广西 `国家专项` 分数组合，因此北科大广西 `国家专项` 现阶段属于“分数侧公开、计划侧不公开”的不对称状态，后续不必再按同一低成本角度盲试其专项计划接口。

- 新增补齐一条 **中国石油大学（华东）保送生过程通知链**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净新增正式页，补出 `2026` 年两条保送生过程通知：
       - `关于公示中国石油大学（华东）2026年保送生拟录取名单的通知` `2026-03-18 09:12:00`
       - `关于中国石油大学（华东）2026年保送生初审结果与校考安排的通知` `2026-03-06 09:30:00`
    2. 同轮再补出 `2025` 年对应两条过程通知：
       - `关于公示中国石油大学（华东）2025年保送生拟录取名单的通知` `2025-03-17 12:42:00`
       - `关于中国石油大学（华东）2025年保送生初审结果与校考安排的通知` `2025-03-05 18:12:00`
  - 价值：
    1. 这一步把华东石油的保送生子线从“只有 `2025/2026` 简章”推进成“简章 + 初审结果与校考安排 + 拟录取名单”的三层结构。
    2. 也让 `2025-2026` 两年保送生过程节奏具备直接对照基础，后续更适合比对学校侧特殊类型发布链的流程稳定性。

- 新增补齐一组 **中国石油大学（华东）高水平运动队过程通知链**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净新增正式页，补出 `2023` 年三条高水平运动队过程通知：
       - `关于公布2023年高水平运动队单独招生文化课考试合格线的通知` `2023-05-25 20:58:00`
       - `关于公示中国石油大学（华东）2023年高水平运动队入选考生名单的通知` `2023-05-25 15:38:00`
       - `关于公示中国石油大学（华东）2023年高水平运动队初审合格名单的通知` `2022-12-31 19:45:00`
    2. 同轮再补出 `2022` 年四条过程通知：
       - `关于公示中国石油大学（华东）2022年高水平运动队乒乓球项目入选考生名单的通知` `2022-06-26 15:35:00`
       - `关于公布2022年高水平运动队单独招生文化课考试合格线的通知` `2022-06-26 10:36:00`
       - `关于公示中国石油大学（华东）2022年高水平运动队校测入选考生名单的通知` `2022-05-09 18:02:00`
       - `关于公布中国石油大学（华东）2022年高水平运动队初审合格名单的通知` `2022-01-14 07:27:00`
    3. 同轮再补出 `2021` 年四条过程通知：
       - `关于公布2021年高水平运动队单独招生文化课考试合格线的通知` `2021-05-21 12:58:00`
       - `关于公示中国石油大学（华东）2021年高水平运动队入选考生名单的通知` `2021-01-22 17:07:00`
       - `关于公布中国石油大学（华东）2021年高水平运动队文化课测试合格名单的通知` `2021-01-16 08:40:00`
       - `关于公示中国石油大学（华东）2021年高水平运动队初审合格名单的通知` `2021-01-11 16:05:00`
  - 价值：
    1. 这一步把华东石油的高水平运动队子线从“只有 `2021-2023` 简章”推进成“简章 + 初审 + 文化课结果 + 入选名单”的四层过程链。
    2. 也让 `2021-2023` 三年高水平运动队过程节奏具备直接对照基础，学校侧特殊类型证据链更接近完整流程而不只是发布入口。

- 新增补齐一组 **中国石油大学（华东）音乐学过程通知链**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净新增正式页，补出 `2021` 年两条音乐学过程通知：
       - `关于公布中国石油大学（华东）2021年音乐学专业分省分方向招生计划的通知` `2021-06-21 19:46:00`
       - `关于公布中国石油大学（华东）2021年音乐学专业山东省生源合格考生名单的通知` `2021-06-18 18:09:00`
    2. 同轮再补出 `2020` 年三条过程通知：
       - `关于公示中国石油大学（华东）2020年音乐学专业招生合格考生名单的通知` `2020-05-07 16:35:00`
       - `关于中国石油大学（华东）2020年音乐学专业招生复试安排的通知` `2020-01-19 16:28:00`
       - `关于公布中国石油大学（华东）2020年音乐学专业招生初试结果的通知` `2020-01-19 16:22:00`
    3. 同轮再补出 `2019` 年三条过程通知：
       - `关于公示中国石油大学（华东）2019年音乐学专业招生合格考生名单的通知` `2019-03-04 02:58:00`
       - `关于中国石油大学（华东）2019年音乐学专业招生复试安排的通知` `2019-01-26 20:20:00`
       - `关于公示中国石油大学（华东）2019年音乐学专业招生复试名单的通知` `2019-01-26 20:12:00`
    4. 同轮再补出 `2018` 年两条过程通知：
       - `关于公示中国石油大学（华东）2018年音乐学专业招生合格考生名单的通知` `2018-03-14 10:44:00`
       - `关于公示中国石油大学（华东）2018年音乐学专业招生复试名单的通知` `2018-02-01 11:42:00`
  - 价值：
    1. 这一步把华东石油的音乐学子线从“只有 `2019-2025` 简章”推进成“简章 + 招生计划 / 初试结果 / 复试安排 / 复试名单 / 合格名单”的多层过程链。
    2. 也让 `2018-2021` 四年音乐学过程节奏具备直接对照基础，进一步增强学校侧艺术类长期发布时间线的可比性。

- 新增补齐一组 **中国石油大学（华东）综合评价过程通知链**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净新增正式页，补出 `2026/2024/2023` 三条综合评价过程通知：
       - `关于中国石油大学（华东）2026年综合评价招生报名相关事宜的提醒` `2026-05-07 10:20:00`
       - `关于中国石油大学（华东）2024年综合评价招生现场考核（面试）安排的通知` `2024-06-03 20:10:00`
       - `关于延长2023年综合评价招生报名时间的通知` `2023-05-10 09:06:00`
    2. 同轮再补出 `2021/2020` 两条综合评价招生入选名单通知：
       - `关于公示中国石油大学（华东）2021年综合评价招生入选考生名单的通知` `2021-06-23 18:33:00`
       - `中国石油大学（华东）关于公示2020年综合评价招生入选考生名单的通知` `2020-07-20 18:14:00`
  - 价值：
    1. 这一步把华东石油的综合评价入选名单子线从原来的 `2022-2025` 补长为连续 `2020-2025`。
    2. 也把综合评价子线继续从“初审 + 入选结果”推进到“报名提醒 / 报名延期 / 面试安排 / 初审 / 入选结果”的更完整过程链。

- 新增补齐一组 **中国石油大学（华东）高水平运动队边界 / 过程通知**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-18` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净新增正式页，补出 `2023/2021/2020` 三年四条关键边界或过程通知：
       - `中国石油大学（华东）关于停止高水平运动队招生的公告` `2023-12-18 11:41:00`
       - `关于中国石油大学（华东）2023年高水平运动队招生（田径、乒乓球项目）现场资格审查的通知` `2023-05-17 17:40:00`
       - `关于提醒相关考生严格遵守招生考试疫情防控要求的公告` `2021-01-11 16:08:00`
       - `关于公布2020年高水平运动队单独招生文化课考试合格线的通知` `2020-07-25 10:37:00`
  - 价值：
    1. 这一步把华东石油高水平运动队子线从“正常流程结果链”进一步推进到“停招边界 + 资格审查 + 防疫要求 + 文化课结果”的更完整过程边界链。
    2. 后续再看华东石油高水平运动队历史变化时，不只是能看到结果，还能直接对照学校侧何时停招、何时做资格审查和现场要求调整。

- 新增补齐一组 **中国石油大学（华东）剩余特殊类型边界 / 结果通知**：
  - 复用缓存：`raw_data/official_followup/zhongguo_shiyou_huadong_211/upc_specialtype_full_lists_20260518.json`
  - `2026-05-19` 本地整理新增确认：
    1. 继续从同一份学校侧官方长列表缓存里筛净最后一批仍然像正式流程页的剩余条目，补出 `艺术类` 三条边界或调整通知：
       - `中国石油大学（华东）2020年音乐学专业复试调整方案` `2020-04-08 16:03:00`
       - `中国石油大学（华东）关于推迟2020年音乐学专业复试及高水平运动队招生选拔工作的通知` `2020-02-01 13:50:00`
       - `关于音乐学专业报考的温馨提示` `2019-01-10 23:24:00`
    2. 同轮再补出 `港澳台招生` 一条正式结果通知：
       - `关于公示中国石油大学（华东）2021年招收台湾地区高中毕业生拟录取名单的通知` `2021-05-21 11:56:00`
  - 价值：
    1. 这一步把华东石油 `音乐学` 与 `港澳台招生` 两条子线里剩余、仍具流程价值的正式页基本收齐，不再只保留主干简章与结果页。
    2. 到这里，华东石油这份学校侧特殊类型长列表缓存里真正有招生流程价值的正式页已经被吃得比较干净，后续继续从同一缓存里再挖的边际收益会明显下降。

# 登录后抓取流程

如果你已经能登录广西阳光志愿系统，我们可以直接复用你的登录态抓指定页面。

## 最短路线

1. 在浏览器里登录 `zyfz.gxeea.cn`
2. 打开你想抓的页面，比如：
   - `招生计划`
   - `选院校`
   - `投档分数明细`
3. 按 `F12` 打开开发者工具
4. 任选一种方式把登录态给我

## 方式 A：复制 Cookie

这是最简单的。

1. 打开开发者工具里的 `Network`
2. 刷新当前页面
3. 点开当前页面对应的主请求
4. 在 `Request Headers` 里找到 `Cookie`
5. 把 `Cookie:` 后面的整段值复制出来
6. 放进 [cookie_header_template.txt](/Users/don/Documents/New%20project/templates/cookie_header_template.txt:1>)，另存为例如：

```text
configs/zyfz_cookie.txt
```

如果该页面还依赖 `Referer` 或其他头，再把它们写进 [request_headers_template.json](/Users/don/Documents/New%20project/templates/request_headers_template.json:1>) 的副本，比如：

```text
configs/zyfz_headers.json
```

## 方式 B：复制为 cURL

如果你不想手动找 `Cookie`：

1. 在 `Network` 里右键页面请求
2. 选择 `Copy` -> `Copy as cURL`
3. 把内容发我或存到仓库里

这一种最稳，因为它把请求头带得最全。

## 如何运行

如果你已经有：

- `configs/zyfz_cookie.txt`
- 可选的 `configs/zyfz_headers.json`

就可以直接跑：

```bash
python3 scripts/fetch_session_url.py \
  --url "https://zyfz.gxeea.cn/你要抓的页面地址" \
  --output raw_data/2026/session_page.html \
  --cookie-file configs/zyfz_cookie.txt \
  --headers-json configs/zyfz_headers.json \
  --insecure
```

说明：

- `--insecure` 主要是给当前这个站点的 SSL 兼容问题留后路。
- 运行结果会写到 `reports/session_fetch_status.csv`。

## 抓哪些页面最值

优先抓：

1. `2026` 本科普通批物理类 `招生计划`
2. `2025` 本科普通批物理类 `选院校` 结果页
3. `2024` 本科普通批物理类 `选院校` 结果页
4. 某个目标院校的 `投档分数明细`

## 当前限制

- 我现在没有你的浏览器登录态，所以不能直接越过登录去抓。
- 一旦你把 `Cookie` 或 `Copy as cURL` 结果给到仓库里，我就能继续跑。

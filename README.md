# AlphaKit · 投研技能库

独立的中英文金融投研技能目录。静态网站包含双语搜索、工作场景和来源仓库筛选、任务组合、技能详情、最多三个技能比较和浏览器本地清单。

源码和发布资源位于 dist/。目录来自公开原始技能仓库的固定版本，保留原作者、许可证、依赖、输入、产物和实际执行未验证的状态。公开文件不包含 AlphaEngine 账号通知、积分、私有路径或访问凭据。

本地预览：

    python3 -m http.server 5188 --bind 127.0.0.1 --directory dist

检查 JavaScript：

    node --check dist/app.js

浏览器验收使用隔离的 headless Chromium，不操作用户已有浏览器。

目录数据的 sources 记录每个原作的固定 commit、归档 SHA-256 与许可证文件。每条 skills 记录对应源文件与至少两条逐字核对的证据引文。增补条目先写到外部机器草稿，经内容复核后用 qa/merge-catalog.py 合入；qa/verify-catalog.py 对每个固定归档核验来源、许可、双语字段、相同文件和私有数据。

来源核验：

    python3 qa/verify-catalog.py <source-archive-directory>

浏览器验收：

    NODE_PATH=<bundled-node-modules> node qa/browser-check.cjs

发布使用 Sites 的 source workflow helper，保持 .openai/hosting.json 中的站点身份和访问范围。目录当前为固定来源的精选版本，没有声明已接通实时采集或自动部署。来源核验与实际执行验证分开记录，未经试跑不标记为实测可用。

# 贡献与维护边界

## 提交新目录条目

请通过 Pull Request 提议新增或修订条目，并提供：

- 原始 GitHub 仓库、固定 commit，以及对应的 `SKILL.md` 路径。
- 仓库许可证、适用的子目录许可证和必须保留的 `NOTICE` 文件。
- 至少两个能在固定源文件中逐字找到的引用，支持目录中的关键描述。
- 有代表性的输入输出示例、必要依赖、宿主或数据限制，以及明确的未验证事项。
- 中文和英文描述。英文内容不得混入中文，且两种语言必须表达同一含义。

不要提交凭据、个人数据、无法确认许可的材料、把第三方作者描述成背书者的内容，或收益保证。维护者会检查原始文件、固定版本、归档哈希、适用许可证、引用、目录模式和浏览器表现。自动审核通过仍不代表技能实际执行已验证。

## 常用本地检查

```sh
python3 scripts/fetch_sources.py --archive-dir .cache/sources
python3 qa/verify-catalog.py .cache/sources
node --check dist/app.js
npm ci
npx playwright install chromium
BASE_URL=http://127.0.0.1:5188/ node qa/browser-check.cjs
```

若要查看 GitHub Pages 子路径表现，先将 `dist/` 挂载到本地服务的 `/AlphaKit/`，再把 `BASE_URL` 指向该路径。`BROWSER_EXECUTABLE_PATH` 可指定 Chromium。不要提交 `.cache/`、`node_modules/`、`.site-qa/` 或本地收据。

## 自动维护边界

GitHub 是唯一维护源。`Update catalog` 工作流每天 `00:45 UTC`（上海时间 `08:45`）运行，也可由维护者手动触发。每轮最多新增 3 条技能、最多复核 12 个候选；一次运行涉及超过 6 条现有技能来源发生变化时应停止并转人工审查。已拒绝候选按内容哈希记账，内容不变时不会每天重复消耗审核额度。所有收录中的来源每日跟踪更新。供应商为 `GLM-5.3-flash` Coding Plan：模型生成双语描述后，另一次独立审核检查证据、准确性和限制。没有付费备用供应商；密钥或模型服务失败时该轮失败。源仓库根许可证变化也会停止发布并转人工审查。

提交目录前还必须通过原始仓库固定 commit、归档 SHA-256、实际 `SKILL.md`、许可证、模式与引用校验，并通过网站根路径和 `/AlphaKit/` 浏览器验收。成功后工作流提交公开目录、`maintenance/ledger.jsonl` 和 `dist/data/update-status.json`，然后触发 Pages 部署。完整逐轮收据和浏览器报告作为 GitHub Actions artifact 保存。失败时不提交候选目录，线上仍保留上一版。

日常没有新增条目时，成功的 no-change 收据仍是一次健康验证。失败由 GitHub Actions 原生失败通知呈现，不另发邮件。新增维护机制可通过 PR 提议；它不得自行改变 schedule、secrets、workflow 权限或自动收录边界。此类改变需维护者审阅对应的工作流和策略文件。

## 许可与使用

根目录 MIT 许可仅覆盖 AlphaKit 原创代码、策展和原创双语描述。收录的第三方技能继续采用原作者许可证。对外分发第三方技能时保留版权、原许可证和所需 `NOTICE`。本仓库只整理目录，不自动安装或执行外部技能，也不自动交易或代用户向平台上传技能。

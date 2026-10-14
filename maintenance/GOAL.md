# AlphaKit 维护目标

## 业务北极星

每次发布的目录均无许可证、来源或模式错误，并且 GitHub canonical catalog 与公开页面内容一致。站点可搜索和浏览技能，但目录来源核验不等于运行验证、官方认证、收益承诺或执行性能承诺。

## 权威与发布链

GitHub 仓库是唯一维护源。GitHub Pages 是主公开站；旧版 FinSkills Hub 继续公开，每次读取 GitHub 的 canonical catalog。

每日 `00:45 UTC`（上海时间 `08:45`），`Update catalog` 工作流最多尝试新增 3 条技能，整轮最多复核 12 个候选；已拒绝且内容未变的候选不会每天重复送审，已收录来源仍每日跟踪。自动流程用 GLM-5.3-flash Coding Plan 生成双语描述，并调用独立的第二轮审核；没有付费备用供应商。模型服务或密钥不可用时该轮失败，不以未审查结果替代。

发布前须检查原始仓库、固定 commit、归档 SHA-256、实际 `SKILL.md`、适用许可证和 `NOTICE`，并验证模式与逐字引用。新增上限为每轮 3 条，候选最多复核 12 个；已拒绝且内容哈希未变的候选不会每天重新送审。所有已收录来源每天跟踪。现有条目的来源在全轮累计发生超过 6 项变化时停止整轮并转人工审核；源仓库根许可证变化也停止发布。之后重建索引，检查 JavaScript，并在 `/` 和 `/AlphaKit/` 两种挂载路径运行浏览器验收。全部通过后才提交目录、公开 ledger 和 `update-status.json`，再触发 Pages 部署。候选校验失败不覆盖当前发布版本。

## 运行信号

`maintenance/ledger.jsonl` 记录公开的每轮状态，`dist/data/update-status.json` 提供站点可读取的最近状态；完整收据和浏览器报告保存在 GitHub Actions artifact。即使没有目录变化，成功的每日 no-change 收据也代表该轮健康校验完成。失败使用 GitHub Actions 原生通知，不发送额外邮件。

本文描述的是维护机制和验收目标，不据此声称自动流程已完成生产实跑。实际投产状态以对应 GitHub Actions 运行、artifact、提交和 Pages readback 为证据。

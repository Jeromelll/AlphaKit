# AlphaKit 自用技能公开候选

本页介绍本仓库提供的三项原创投研技能。技能目录中的固定提交用于定位版本；本地调用从完整技能文件夹开始。

| 技能 | 中文用途 | 适用场景 | 主要输入与输出 |
|---|---|---|---|
| [incremental-business-sizing](../skills/incremental-business-sizing/SKILL.md) | 把新业务机会拆成可复算的收入、利润与 EPS 驱动链 | 产能释放、商业化率、付费订阅、交易抽佣和业务上限测算 | 带单位、期间、来源的 JSON 假设；输出情景结果、缺口诊断和敏感性矩阵 |
| [sellside-model-exhibits](../skills/sellside-model-exhibits/SKILL.md) | 把同一份结果做成计算桥、情景表与敏感性表 | 研究报告、模型说明、文档原生表格和静态图 | 上一项的 results.json；输出 HTML、PNG、Excel、审计 XML 和飞书表格片段 |
| [pre-trade-quick-brief](../skills/pre-trade-quick-brief/SKILL.md) | 快速解释新股票的叙事变化、业绩上限与前瞻估值 | 新股票初筛、走势不错但未研究、主题排名 | 公司及已授权原始资料；输出结论、时间窗、估值条件与反证 |

## 安装

取得经确认的公开版本后，将 `skills/` 下所需的完整同名文件夹放入宿主支持的自定义技能目录。文件夹内应保留 SKILL.md、scripts、references、assets（如有）、agents 和 LICENSE。如已有同名技能，先检查版本和本地修改，再按宿主安装机制处理；不要把两个版本的文件混在同一目录。

增量测算引擎只使用 Python 标准库。渲染器还需 Pillow、openpyxl 和能显示中文的系统字体。本轮离线验收环境为 Python 3.13.12、Pillow 12.3.0、openpyxl 3.1.5；其他宿主的自动发现和调用尚未实测。

安装前可在此目录运行合成示例。Python 依赖需由使用者按自身环境管理，技能不会联网安装软件或检索数据。

## 示例

```sh
python3 skills/incremental-business-sizing/scripts/size_opportunity.py --input skills/incremental-business-sizing/assets/synthetic-capacity-2030.json --out results.json
python3 skills/sellside-model-exhibits/scripts/render_exhibits.py --input results.json --outdir rendered
```

所有示例数据均为原创合成数据。基准情景采用数量 100 × 单价 20＝收入 2,000；经营利润率 25%、税率 20%、股数 100 时，EPS 为 4。数量和价格的双变量矩阵由同一计算图重算。

把输入换成 `synthetic-missing-shares.json`，基准情景股数与 EPS 保持未知，收入与利润仍可计算。空模板 `new-opportunity-template.json` 用于新任务，应复制到工作目录后填写。

渲染结果包括 `exhibits.html`、`bridge.png`、`sensitivity_revenue.png`、`exhibits.xlsx`、`exhibits.xml` 和 `feishu.xml`。生成 Excel 公式并设置打开重算，不等于已经在 Microsoft Excel 内重算。

## 来源与许可方案

候选由用户自有技能整理，运行脚本保持源版本不变，文档和样例经过公开化处理。两个卖方报告复算 JSON、报告案例说明和带报告样例的原测试文件均未放入候选。快速初研改为自包含方法，未携带私人路径、书籍原文、书籍脚本或内部知识库依赖。

本仓库中的原创公开整理内容使用随包 MIT 许可证；此前私用源版本未附单独许可，不据此改称源版本已采用 MIT。第三方 Python 依赖未随包复制，继续受各自许可证约束。候选不含研报 PDF、机构标识、研究持仓、用户模型、凭据或内部记忆。

# AlphaKit · 投研技能库

AlphaKit 是面向金融与投资研究工作流的中英文技能目录。目录按公开原始仓库和固定版本整理，展示原作者、许可证、依赖、输入输出、示例与逐字来源证据。它帮助读者发现和评估技能，不代表 AlphaKit 已实际运行这些技能。

## 访问与数据

- 主站：[AlphaKit GitHub Pages](https://jeromelll.github.io/AlphaKit/)
- 维护仓库：[github.com/Jeromelll/AlphaKit](https://github.com/Jeromelll/AlphaKit)
- 完整技能索引：[docs/CATALOG.md](docs/CATALOG.md)；结构化目录：[catalog.json](dist/data/catalog.json)
- 现有 [AlphaKit 站点](https://finskills-hub.fit-lemon-8083.chatgpt.site) 继续公开；该站每次读取 GitHub 上的权威目录，获取失败时显示标有核验日期的随站副本。GitHub 仓库是唯一维护源。

技能和来源仓库数量会随审核结果变化，请以 `docs/CATALOG.md` 和网站当前目录为准，不依赖固定数量。每条记录分别标注来源核验与实际执行状态；`sourceVerified: true` 表示来源、版本、许可和引用已核对，`executionVerified: false` 表示 AlphaKit 没有验证技能在宿主环境中的实际运行效果。目录不提供官方认证、收益或执行性能承诺。

## 本地开发

静态站点文件在 `dist/`。Python 3 用于来源处理，Node.js 用于浏览器验收。

```sh
python3 -m http.server 5188 --bind 127.0.0.1 --directory dist
```

在另一个终端运行浏览器检查：

```sh
npm ci
npx playwright install chromium
BASE_URL=http://127.0.0.1:5188/ node qa/browser-check.cjs
```

`BASE_URL` 可设置为部署子路径，例如 `http://127.0.0.1:5188/AlphaKit/`。`BROWSER_EXECUTABLE_PATH` 可指定已有的 Chromium 可执行文件。来源和目录验证使用已固定的归档：

```sh
python3 scripts/fetch_sources.py --archive-dir .cache/sources
python3 qa/verify-catalog.py .cache/sources
```

生成待审查更新的命令如下。它每轮最多尝试新增 3 条、复核 12 个候选；已拒绝且内容未变的候选不会每天重复送审。只有通过来源、许可、模式和两轮独立审核的条目才进入暂存目录：

```sh
python3 scripts/update_catalog.py --write --max-items 3 --archive-dir .cache/sources --receipt artifacts/update.json
python3 scripts/build_index.py
```

`Update catalog` 工作流每天 `00:45 UTC`（上海时间 `08:45`）运行，使用 GLM-5.3-flash Coding Plan 生成双语描述，并做独立的第二轮审核；没有付费备用供应商。自动更新还会执行目录验证、JavaScript 语法检查以及根路径和 `/AlphaKit/` 两种浏览器验收，通过后才提交目录、公开 ledger 和 `update-status.json`，并触发 GitHub Pages 部署。候选校验失败会保留上一版。具体字段和人工维护流程见 [docs/CATALOG.md](docs/CATALOG.md)。日常健康收据和失败边界见 [maintenance/GOAL.md](maintenance/GOAL.md) 与 [maintenance/NO_WINDOW.md](maintenance/NO_WINDOW.md)。

## 使用与许可

AlphaKit 默认建议从原始仓库获取所需技能，并遵循对应宿主的安装说明。安装或再分发时保留原作者版权、原许可证及其要求的 `NOTICE` 文件。目录维护程序只处理公开来源和说明，不运行第三方技能脚本或发起交易。使用者应先检查来源、权限、依赖和风险，并在自己的环境中试跑。

根目录 [LICENSE](LICENSE) 适用于 AlphaKit 自有代码、策展工作和原创双语描述。目录包含独立的第三方作品；第三方 MIT、Apache-2.0 等原作继续受各自许可证约束。根目录 MIT 许可不改变第三方许可证，也不覆盖第三方原文、引用、商标或其他受保护材料。

## 贡献

新收录建议通过 Pull Request 提交，并提供原始仓库和固定版本、可核验的 `SKILL.md` 路径、许可证及必要的 `NOTICE`、具体示例和依赖。维护者会检查来源归属、引用准确性、双语内容和边界表述。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

本仓库提供的三项原创投研技能、安装方式与合成示例见 [原创投研技能](docs/RESEARCH_SKILLS.md)。

# AlphaKit · Investment Research Skills

AlphaKit is a bilingual directory of skills for finance and investment research workflows. Entries point to public original repositories and pinned revisions, and describe the author, license, dependencies, inputs, outputs, examples, and exact source evidence. The directory helps readers discover and assess skills; it does not mean AlphaKit has run them.

## Site and data

- Main site: [AlphaKit on GitHub Pages](https://jeromelll.github.io/AlphaKit/)
- Maintainer repository: [github.com/Jeromelll/AlphaKit](https://github.com/Jeromelll/AlphaKit)
- Complete skill index: [docs/CATALOG.md](docs/CATALOG.md); structured catalog: [catalog.json](dist/data/catalog.json)
- The existing [AlphaKit site](https://finskills-hub.fit-lemon-8083.chatgpt.site) remains public and reads the canonical catalog from GitHub on each visit. When GitHub cannot be reached it displays a dated bundled copy. The GitHub repository is the single maintenance source.

Skill and repository counts can change as entries are reviewed. Use `docs/CATALOG.md` and the live catalog rather than relying on fixed counts. Each entry reports source review separately from execution status. `sourceVerified: true` means the source, revision, license, and quotations were checked. `executionVerified: false` means AlphaKit has not verified the skill in its host environment. The directory makes no claim of official certification, returns, or execution performance.

## Local development

The static site is in `dist/`. Source processing uses Python 3; browser verification uses Node.js.

```sh
python3 -m http.server 5188 --bind 127.0.0.1 --directory dist
```

In another terminal, run browser verification:

```sh
npm ci
npx playwright install chromium
BASE_URL=http://127.0.0.1:5188/ node qa/browser-check.cjs
```

Set `BASE_URL` to a deployment subpath when needed, such as `http://127.0.0.1:5188/AlphaKit/`. Set `BROWSER_EXECUTABLE_PATH` to use an existing Chromium executable. Verify the catalog against its pinned archives with:

```sh
python3 scripts/fetch_sources.py --archive-dir .cache/sources
python3 qa/verify-catalog.py .cache/sources
```

The following command prepares an update. It attempts at most three new skills; only entries that pass source, license, schema, and two independent review checks reach the staged catalog:

```sh
python3 scripts/update_catalog.py --write --max-items 3 --archive-dir .cache/sources --receipt artifacts/update.json
python3 scripts/build_index.py
```

The `Update catalog` workflow runs daily at `00:45 UTC` (`08:45` Shanghai time). It uses the GLM-5.3-flash Coding Plan to draft bilingual entries, followed by an independent second review; there is no paid fallback provider. Each run attempts at most three new skills and reviews no more than 12 candidates. Rejected candidates with unchanged content are not sent for review again each day; all accepted sources continue to be checked daily. The workflow also validates the catalog, checks JavaScript syntax, and runs browser verification at both the site root and `/AlphaKit/`. Only after these checks pass does it commit the catalog, public ledger, and `update-status.json`, then trigger a GitHub Pages deployment. A failed candidate batch leaves the previous published version in place. See [docs/CATALOG.md](docs/CATALOG.md) for the field definitions and contribution flow. Daily health receipts and failure boundaries are described in [maintenance/GOAL.md](maintenance/GOAL.md) and [maintenance/NO_WINDOW.md](maintenance/NO_WINDOW.md).

## Use and licensing

By default, obtain a skill from its original repository and follow the installation instructions for your host. Preserve the original copyright, license, and any required `NOTICE` when installing or redistributing it. The catalog updater only processes public sources and descriptions; it does not execute collected scripts or place trades. Review source, permissions, dependencies, and risks, then test the skill in your environment.

The root [LICENSE](LICENSE) applies to AlphaKit's own code, curation work, and original bilingual descriptions. Third-party works in the catalog remain under their own licenses, including MIT and Apache-2.0. The root MIT license does not change third-party terms or cover third-party text, quotations, trademarks, or other protected material.

## Contributing

Propose new entries by Pull Request with the original repository and pinned revision, a verifiable `SKILL.md` path, license and any required `NOTICE`, a concrete example, and dependencies. Maintainers review attribution, quotation accuracy, bilingual content, and stated limits. See [CONTRIBUTING.md](CONTRIBUTING.md).

The three original research skills, installation instructions and synthetic examples are documented in [Original research skills](docs/RESEARCH_SKILLS.md).

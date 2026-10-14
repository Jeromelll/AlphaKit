"""Build the repository's readable skill index from the website's single catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = {'research': '公司与行业研究 / Company research', 'earnings': '财报分析 / Earnings',
              'valuation': '估值与建模 / Valuation & models', 'portfolio': '组合与风险 / Portfolio',
              'deals': '交易与尽调 / Deals & diligence', 'operations': '研究流程 / Operations',
              'data': '金融数据 / Financial data', 'macro': '宏观与市场 / Macro & markets',
              'quant': '量化与技术研究 / Quant research', 'fixedincome': '固收与信用 / Fixed income'}


def clean(value):
    return value.replace('|', '\\|').replace('\n', ' ')


def main():
    catalog = json.loads((ROOT / 'dist/data/catalog.json').read_text())
    lines = ['# AlphaKit 技能索引 / Skill index', '',
             '由同一份网站目录自动生成。Generated from the website catalog.', '',
             f"{len(catalog['skills'])} skills · {len(catalog['sources'])} original repositories · {catalog['updatedAt']}", '',
             '收录表示原文件与许可证已核对，实际执行未验证。Inclusion means source and license checks; execution is unverified.', '']
    for category, title in CATEGORIES.items():
        skills = [s for s in catalog['skills'] if s['category'] == category]
        if not skills:
            continue
        lines.extend(['## ' + title, '', '| 技能 / Skill | 来源 / Source | License |', '| --- | --- | --- |'])
        for skill in skills:
            lines.append(f"| [{clean(skill['name'])}]({skill['sourceUrl']})<br>{clean(skill['nameEn'])} | "
                         f"[{clean(skill['author'])}]({skill['repository']}) | {skill['license']} |")
        lines.append('')
    target = ROOT / 'docs/CATALOG.md'
    target.parent.mkdir(exist_ok=True)
    target.write_text('\n'.join(lines) + '\n')
    print(json.dumps({'indexedSkills': len(catalog['skills'])}))


if __name__ == '__main__':
    main()

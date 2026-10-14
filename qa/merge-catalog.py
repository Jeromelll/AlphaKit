"""Merge reviewed additions while retaining the existing catalog and attribution."""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

site = Path(__file__).resolve().parent.parent
evidence_dir = Path(sys.argv[1])
catalog_path = site / 'dist/data/catalog.json'
catalog = json.loads(catalog_path.read_text())
by_id = {s['id']: s for s in catalog['skills']}
for addition_path in sys.argv[2:]:
    addition = json.loads(Path(addition_path).read_text())
    for skill in addition['skills']:
        if skill['id'] in by_id:
            old = by_id[skill['id']]
            assert (old['repository'], old['sourcePath']) == (skill['repository'], skill['sourcePath'])
        by_id[skill['id']] = skill
catalog['skills'] = list(by_id.values())
assert len({(s['repository'], s['sourcePath']) for s in catalog['skills']}) == len(catalog['skills'])
descriptions = {
    'anthropics/financial-services': (
        '财报、估值、投行、基金运营与私募股权工作流；原始宿主为 Claude Code / Cowork。',
        'Earnings, valuation, investment banking, fund administration and private-equity workflows for Claude Code and Cowork.'),
    'RKiding/Awesome-finance-skills': (
        'AlphaEar 的财经检索、新闻、行情、情绪、信号和预测技能，使用包内脚本与模型资源。',
        'AlphaEar skills for financial search, news, market data, sentiment, signals and forecasting, with supporting scripts and model resources.'),
    'himself65/finance-skills': (
        '面向 AI 研究代理的金融数据、财报、估值、期权和市场分析技能，明确列出外部服务要求。',
        'Financial data, earnings, valuation, options and market-analysis skills for AI research agents, with explicit external-service requirements.'),
    'Geeksfino/finskills': (
        '面向中国与美国市场的财报分析、选股、行业轮动、数据和组合检查，按市场区分数据与方法。',
        'Financial analysis, screening, sector rotation, data and portfolio reviews for Chinese and US markets, with market-specific methods and data.'),
    'questflowai/investorskills': (
        '仓库作者整理的投资判断、价值研究和专项调查框架，保留每种方法的适用范围。',
        'Repository-authored frameworks for investment judgment, value research and specialist investigations, with each method’s scope retained.'),
    'star23/Day1Global-Skills': (
        '科技股财报深挖、美国价值投资、市场情绪与宏观流动性研究方法。',
        'Research methods for technology earnings, US value investing, market sentiment and macro liquidity.')
}
sources = []
for repository in dict.fromkeys(s['repository'] for s in catalog['skills']):
    repo = repository.removeprefix('https://github.com/')
    manifest = json.loads((evidence_dir / (repo.replace('/', '--') + '.json')).read_text())
    archive = evidence_dir / manifest['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archiveSha256']
    group = [s for s in catalog['skills'] if s['repository'] == repository]
    assert all(s['commit'] == manifest['commit'] for s in group)
    root_license = manifest.get('licensePath', 'LICENSE')
    with zipfile.ZipFile(archive) as z:
        root = z.namelist()[0].split('/')[0] + '/'
        root_data = z.read(root + root_license)
        license_id = 'MIT' if b'Permission is hereby granted' in root_data else 'Apache-2.0'
        assert license_id in ('MIT', 'Apache-2.0')
        retained = {root_license}
        retained.update(p for p in manifest['licensePaths'] if str(Path(p).parent) == '.' and Path(p).name.lower().startswith('notice'))
        for skill in group:
            assert skill['license'] == license_id
            path = Path(skill['sourcePath'])
            assert skill['sourcePath'] in manifest['skillPaths']
            if repo == 'anthropics/financial-services':
                assert skill['sourcePath'].startswith('plugins/vertical-plugins/'), skill['id']
            ancestors = {str(p) for p in path.parents}
            relevant = [p for p in manifest['licensePaths'] if str(Path(p).parent) in ancestors]
            retained.update(relevant)
            effective = sorted([p for p in relevant if Path(p).name.lower().startswith('license')], key=lambda p: len(Path(p).parts))
            license_path = effective[-1] if effective else root_license
            local_data = z.read(root + license_path)
            assert (b'Apache' in local_data and b'2.0' in local_data) if license_id == 'Apache-2.0' else b'Permission is hereby granted' in local_data
            skill['licenseUrl'] = repository + '/blob/' + skill['commit'] + '/' + license_path
        license_files = []
        for license_path in sorted(retained):
            if repo == 'anthropics/financial-services' and license_path == 'LICENSE':
                filename = 'anthropic-financial-services-LICENSE.txt'
            else:
                filename = repo.replace('/', '--') + '--' + re.sub(r'[^\w.-]', '--', license_path)
            output = site / 'dist/licenses' / filename
            output.parent.mkdir(exist_ok=True)
            output.write_bytes(z.read(root + license_path))
            license_files.append({'sourcePath': license_path, 'file': '/licenses/' + filename})
        root_file = next(l['file'] for l in license_files if l['sourcePath'] == root_license)
    zh, en = descriptions[repo]
    sources.append({'repository': repository, 'commit': manifest['commit'], 'license': license_id,
                    'licensePath': root_license, 'licenseFile': root_file, 'licenseFiles': license_files,
                    'archive': manifest['archive'], 'archiveSha256': manifest['archiveSha256'],
                    'description': zh, 'descriptionEn': en})
catalog['sources'] = sources
catalog['updatedAt'] = '2026-10-14'
catalog['evidence'] = {'checks': {'skills': len(catalog['skills']), 'repositories': len(sources),
                                 'executionTestsRun': 0}, 'method': 'Pinned original files and retained licenses; execution is unverified.'}
catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'skills': len(catalog['skills']), 'repositories': len(sources)}, indent=2))

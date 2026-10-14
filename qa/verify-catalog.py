"""Validate every catalog entry and license against pinned source archives."""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

site = Path(__file__).resolve().parent.parent
catalog = json.loads((site / 'dist/data/catalog.json').read_text())
archives = Path(sys.argv[1])
categories = {'research', 'earnings', 'valuation', 'portfolio', 'deals', 'operations',
              'data', 'macro', 'quant', 'fixedincome'}
text_fields = ('name', 'summary', 'method', 'environment', 'example', 'notes')
array_fields = ('inputs', 'outputs', 'dependencies', 'tags')
skills = catalog['skills']
assert len({s['id'] for s in skills}) == len(skills)
assert len({(s['repository'], s['commit'], s['sourcePath']) for s in skills}) == len(skills)
sources = catalog['sources']
assert len({s['repository'] for s in sources}) == len(sources)
assert set(s['repository'] for s in skills) == set(s['repository'] for s in sources)
matched = 0
licenses_checked = 0
original_hashes = {}
for source in sources:
    archive = archives / source['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == source['archiveSha256']
    assert re.fullmatch(r'[a-f0-9]{40}', source['commit'])
    with zipfile.ZipFile(archive) as z:
        root = z.namelist()[0].split('/')[0] + '/'
        for license_info in source['licenseFiles']:
            data = z.read(root + license_info['sourcePath'])
            assert (site / 'dist' / license_info['file'].lstrip('/')).read_bytes() == data
            licenses_checked += 1
        for s in [s for s in skills if s['repository'] == source['repository']]:
            assert s['commit'] == source['commit']
            assert s['sourceVerified'] is True and s['executionVerified'] is False
            assert s['category'] in categories and s['license'] == source['license']
            assert s['author'].strip() and s['originalName'].strip()
            for name in text_fields:
                for field in (name, name + 'En'):
                    assert isinstance(s[field], str) and s[field].strip(), (s['id'], field)
                    if field.endswith('En'):
                        assert not re.search(r'[\u4e00-\u9fff]', s[field]), (s['id'], field)
            for name in array_fields:
                for field in (name, name + 'En'):
                    assert isinstance(s[field], list) and s[field], (s['id'], field)
                    assert all(isinstance(v, str) and v.strip() for v in s[field])
                    if field.endswith('En'):
                        assert not re.search(r'[\u4e00-\u9fff]', ' '.join(s[field])), (s['id'], field)
            for field in ('sourceUrl', 'repository', 'licenseUrl'):
                url = urlparse(s[field])
                assert url.scheme == 'https' and url.netloc == 'github.com'
            assert s['sourceUrl'] == s['repository'] + '/blob/' + s['commit'] + '/' + s['sourcePath']
            source_path = Path(s['sourcePath'])
            assert '..' not in source_path.parts and not source_path.is_absolute()
            assert source_path.name.lower() == 'skill.md'
            original_bytes = z.read(root + s['sourcePath'])
            original = original_bytes.decode()
            digest = hashlib.sha256(original_bytes).hexdigest()
            assert digest not in original_hashes, (s['id'], original_hashes.get(digest), 'identical original file')
            original_hashes[digest] = s['id']
            assert len(s['evidenceQuotes']) >= 2
            for quote in s['evidenceQuotes']:
                assert quote and quote in original, (s['id'], quote)
                matched += 1
            license_path = s['licenseUrl'].split('/blob/' + s['commit'] + '/')[1]
            license_data = z.read(root + license_path)
            if s['license'] == 'Apache-2.0':
                assert b'Apache' in license_data and b'2.0' in license_data
            elif s['license'] == 'MIT':
                assert b'Permission is hereby granted' in license_data
            else:
                raise AssertionError(('Unhandled license', s['id']))
            assert license_path in [l['sourcePath'] for l in source['licenseFiles']]
            ancestor_dirs = {str(p) + '/' for p in source_path.parents if str(p) != '.'}
            local_licenses = [n[len(root):] for n in z.namelist() if
                              str(Path(n[len(root):]).parent) + '/' in ancestor_dirs and
                              Path(n).name.lower().startswith(('license', 'notice'))]
            retained = {l['sourcePath'] for l in source['licenseFiles']}
            assert set(local_licenses) <= retained, (s['id'], local_licenses)
public = '\n'.join(p.read_text() for p in (site / 'dist').rglob('*') if p.is_file())
for pattern in (r'/Users/', r'/var/folders/', r'AlphaEngine', r'AlphaClaw',
                r'(?i)(?:api[_-]?key|access[_-]?token|bearer)\s*[=:]\s*[\"\'][^\"\']{16,}'):
    assert not re.search(pattern, public), pattern
report = {'skills': len(skills), 'repositories': len(sources), 'originalFilesFound': len(skills),
          'exactEvidenceQuotesMatched': matched, 'bilingualFieldsChecked': len(skills) * 20,
          'licenseFilesChecked': licenses_checked, 'privateDataScan': 'passed', 'executionTestsRun': 0}
print(json.dumps(report, ensure_ascii=False, indent=2))

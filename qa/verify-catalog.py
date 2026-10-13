"""Validate the curated catalog against its pinned upstream source archive."""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

site = Path(__file__).resolve().parent.parent
catalog = json.loads((site / 'dist/data/catalog.json').read_text())
evidence = catalog['evidence']
archive = Path(sys.argv[1])
assert hashlib.sha256(archive.read_bytes()).hexdigest() == evidence['archiveSha256']
categories = {'research', 'earnings', 'valuation', 'portfolio', 'deals', 'operations'}
text_fields = ('name', 'summary', 'method', 'environment', 'example', 'notes')
array_fields = ('inputs', 'outputs', 'dependencies', 'tags')
skills = catalog['skills']
assert len({s['id'] for s in skills}) == len(skills)
matched = 0
with zipfile.ZipFile(archive) as z:
    entries = z.namelist()
    root = entries[0].split('/')[0] + '/'
    license_bytes = z.read(root + 'LICENSE')
    assert b'Apache License' in license_bytes and b'Version 2.0' in license_bytes
    for s in skills:
        assert s['category'] in categories
        assert s['commit'] == evidence['commit']
        assert s['sourceVerified'] is True and s['executionVerified'] is False
        assert s['author'] == 'Anthropic' and s['license'] == 'Apache-2.0'
        for name in text_fields:
            for field in (name, name + 'En'):
                assert isinstance(s[field], str) and s[field].strip(), (s['id'], field)
        for name in array_fields:
            for field in (name, name + 'En'):
                assert isinstance(s[field], list) and s[field], (s['id'], field)
                assert all(isinstance(v, str) and v.strip() for v in s[field])
        assert s['repository'] == 'https://github.com/anthropics/financial-services'
        expected = s['repository'] + '/blob/' + evidence['commit'] + '/' + s['sourcePath']
        assert s['sourceUrl'] == expected
        assert s['licenseUrl'] == s['repository'] + '/blob/' + evidence['commit'] + '/LICENSE'
        for field in ('sourceUrl', 'repository', 'licenseUrl'):
            url = urlparse(s[field])
            assert url.scheme == 'https' and url.netloc == 'github.com'
        source_path = Path(s['sourcePath'])
        assert '..' not in source_path.parts and s['sourcePath'].startswith('plugins/vertical-plugins/')
        original = z.read(root + s['sourcePath']).decode()
        for quote in s['evidenceQuotes']:
            assert quote in original, (s['id'], quote)
            matched += 1
        ancestor_dirs = {str(p) + '/' for p in source_path.parents if str(p) != '.'}
        overrides = [n[len(root):] for n in entries if
                     str(Path(n[len(root):]).parent) + '/' in ancestor_dirs and
                     Path(n).name.lower().startswith(('license', 'notice'))]
        assert not overrides, (s['id'], overrides)
    assert (site / 'dist/licenses/anthropic-financial-services-LICENSE.txt').read_bytes() == license_bytes
public = '\n'.join(p.read_text() for p in (site / 'dist').rglob('*') if p.is_file())
for pattern in (r'/Users/', r'/var/folders/', r'AlphaEngine', r'AlphaClaw',
                r'(?i)(?:api[_-]?key|access[_-]?token|bearer)\s*[=:]\s*[\"\'][^\"\']{16,}'):
    assert not re.search(pattern, public), pattern
report = {'skills': len(skills), 'originalFilesFound': len(skills),
          'exactEvidenceQuotesMatched': matched, 'bilingualFieldsChecked': len(skills) * 20,
          'license': evidence['license'], 'sourceCommit': evidence['commit'],
          'privateDataScan': 'passed', 'executionTestsRun': 0}
print(json.dumps(report, ensure_ascii=False, indent=2))

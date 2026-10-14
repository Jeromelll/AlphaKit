"""Read GitHub source snapshots without executing third-party code."""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
MAX_ARCHIVE = 80 * 1024 * 1024


def repository_name(url):
    match = re.fullmatch(r'https://github\.com/([\w.-]+/[\w.-]+)', url)
    if not match:
        raise ValueError('Unsupported source repository URL')
    return match.group(1)


def request_bytes(url, token=None, limit=MAX_ARCHIVE, timeout=60):
    headers = {'User-Agent': 'AlphaKit-catalog/1.0', 'Accept': 'application/vnd.github+json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
                data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError('Source exceeds the configured download limit')
            return data
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError('Source request failed: HTTP ' + str(error.code)) from None
        except (TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise RuntimeError('Source request failed or timed out') from None
        time.sleep(2 ** attempt)
    raise RuntimeError('Source request failed')


def github_api(path):
    return json.loads(request_bytes('https://api.github.com/' + path,
                                   os.environ.get('GITHUB_TOKEN'), limit=4 * 1024 * 1024))


def latest_commit(repo):
    metadata = github_api('repos/' + repo)
    branch = urllib.parse.quote(metadata['default_branch'], safe='')
    commit = github_api('repos/' + repo + '/commits/' + branch)['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Invalid GitHub commit')
    return commit


def archive_name(repo, commit):
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo) or not re.fullmatch(r'[a-f0-9]{40}', commit):
        raise ValueError('Invalid source identity')
    return repo.replace('/', '--') + '--' + commit + '.zip'


def fetch_archive(repo, commit, directory, expected_hash=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / archive_name(repo, commit)
    if not target.exists():
        data = request_bytes('https://codeload.github.com/' + repo + '/zip/' + commit)
        target.write_bytes(data)
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if expected_hash and actual != expected_hash:
        raise ValueError('Pinned source archive hash mismatch: ' + repo)
    # Inspect paths and uncompressed sizes; never extract archive members.
    with zipfile.ZipFile(target) as archive:
        total = 0
        for member in archive.infolist():
            path = PurePosixPath(member.filename)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Unsafe archive path')
            total += member.file_size
            if total > 250 * 1024 * 1024:
                raise ValueError('Source uncompressed size exceeds limit')
    return target, actual


class Snapshot:
    def __init__(self, path):
        self.archive = zipfile.ZipFile(path)
        self.root = self.archive.namelist()[0].split('/')[0] + '/'
        self.paths = {name[len(self.root):] for name in self.archive.namelist()
                      if name.startswith(self.root) and not name.endswith('/')}

    def read(self, path):
        if path not in self.paths:
            raise ValueError('Missing source file: ' + path)
        return self.archive.read(self.root + path)

    def skills(self, prefix=''):
        return sorted(path for path in self.paths
                      if path.startswith(prefix) and PurePosixPath(path).name.lower() == 'skill.md')

    def license_paths(self):
        return sorted(path for path in self.paths
                      if PurePosixPath(path).name.lower().startswith(('license', 'notice')))


def license_id(data):
    if b'Permission is hereby granted, free of charge' in data:
        return 'MIT'
    if b'Apache License' in data and b'Version 2.0' in data:
        return 'Apache-2.0'
    raise ValueError('No supported explicit MIT or Apache-2.0 license')


def root_license(snapshot):
    matches = [path for path in snapshot.license_paths()
               if '/' not in path and PurePosixPath(path).name.lower().startswith('license')]
    if not matches:
        raise ValueError('Missing root license')
    for path in matches:
        try:
            return path, license_id(snapshot.read(path))
        except ValueError:
            pass
    raise ValueError('Unsupported root license')


def applicable_licenses(snapshot, source_path, root_path):
    ancestors = {str(parent) for parent in PurePosixPath(source_path).parents}
    paths = [path for path in snapshot.license_paths()
             if str(PurePosixPath(path).parent) in ancestors]
    licenses = [path for path in paths if PurePosixPath(path).name.lower().startswith('license')]
    effective = max(licenses, key=lambda path: len(PurePosixPath(path).parts)) if licenses else root_path
    return effective, set(paths) | {root_path}

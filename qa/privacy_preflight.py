"""Pre-publication check. Run locally before pushing; prints no matched values.

Usage: python3 qa/privacy_preflight.py --range <remote-base>..<local-head>
This checks new commit identities and tracked UTF-8 files; it is not a guarantee
against all private data, and does not rewrite existing history.
"""
import argparse
import json
import re
import subprocess

RULES = {
    'private-key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'credential-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b'),
    'personal-path': re.compile(r'/' + r'Users/[^/\s]+/|/' + r'home/[^/\s]+/|[A-Z]:\\Users\\[^\\\s]+'),
    'credential-url': re.compile(r'https?://[^\s/]+:[^\s/@]+@'),
}

def content_hits(data):
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return ['binary-requires-manual-review']
    return [kind for kind, pattern in RULES.items() if pattern.search(text)]

def identity_hits(raw):
    hits = []
    for field in ('author', 'committer'):
        match = re.search(r'^' + field + r' .*? <([^>]+)>', raw, re.M)
        if not match or not re.fullmatch(r'[^@\s]+@(?:users\.)?noreply\.github\.com', match[1]):
            hits.append(field + '-non-noreply-email')
    message = raw.partition('\n\n')[2]
    for email in re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', message):
        if not re.fullmatch(r'[^@\s]+@(?:users\.)?noreply\.github\.com', email):
            hits.append('commit-message-contact-email')
            break
    return hits

def git(*args):
    return subprocess.check_output(['git', *args])

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--range', help='Explicit base..head, excluding already published commits')
    mode.add_argument('--tree', help='Content-only check of a commit tree')
    args = parser.parse_args()
    if args.range and (not re.fullmatch(r'[A-Za-z0-9_./~-]+\.\.[A-Za-z0-9_./~-]+', args.range) or args.range.startswith('-') or '...' in args.range):
        parser.error('Provide an explicit base..head range')
    if args.tree and not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./~-]*', args.tree):
        parser.error('Provide a valid tree ref')
    findings = []
    commits = git('rev-list', args.range, '--').decode().splitlines() if args.range else []
    for commit in commits:
        for kind in identity_hits(git('cat-file', 'commit', commit).decode('utf8', 'replace')):
            findings.append({'commit': commit, 'type': kind})
    head = args.range.split('..', 1)[1] if args.range else args.tree
    entries = set()
    for ref in [head, *commits]:
        entries.update(git('ls-tree', '-r', '-z', ref).split(b'\0'))
    for entry in sorted(entries):
        if not entry:
            continue
        metadata, path = entry.split(b'\t', 1)
        mode, kind, sha = metadata.decode().split()
        if kind != 'blob':
            findings.append({'path': path.decode(), 'type': 'non-blob-requires-manual-review'})
            continue
        for kind in content_hits(git('cat-file', 'blob', sha)):
            findings.append({'path': path.decode(), 'type': kind})
    print(json.dumps({'findings': findings, 'passed': not findings}, ensure_ascii=False))
    return bool(findings)

if __name__ == '__main__':
    raise SystemExit(main())

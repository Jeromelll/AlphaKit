"""Download the catalog's exact pinned evidence for local or CI validation."""
import argparse
import json
from source_io import ROOT, fetch_archive, repository_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive-dir', default='.cache/sources')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'dist/data/catalog.json').read_text())
    for source in catalog['sources']:
        fetch_archive(repository_name(source['repository']), source['commit'],
                      args.archive_dir, source['archiveSha256'])
    print(json.dumps({'pinnedArchivesVerified': len(catalog['sources'])}))


if __name__ == '__main__':
    main()

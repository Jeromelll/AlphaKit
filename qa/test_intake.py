"""Boundary tests for the bounded AlphaKit intake path."""
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))

import source_io
import update_catalog


COMMIT = 'a' * 40
REPO_NAME = 'example/research-skills'
MIT = b'''MIT License\nPermission is hereby granted, free of charge, to any person obtaining a copy.\n'''


def write_archive(directory, members, repo=REPO_NAME, commit=COMMIT):
    archive_path = Path(directory) / source_io.archive_name(repo, commit)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, 'w') as archive:
        for name, data in members.items():
            archive.writestr('research-skills-main/' + name, data)
    return archive_path


class ArchiveBoundaryTests(unittest.TestCase):
    def test_fetch_archive_rejects_parent_traversal_member(self):
        with tempfile.TemporaryDirectory() as temporary:
            write_archive(temporary, {'../outside.txt': b'no extraction'})
            with self.assertRaisesRegex(ValueError, 'Unsafe archive path'):
                source_io.fetch_archive(REPO_NAME, COMMIT, temporary)

    def test_fetch_archive_rejects_pinned_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = write_archive(temporary, {'SKILL.md': b'safe snapshot'})
            expected = '0' * 64
            self.assertNotEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
            with self.assertRaisesRegex(ValueError, 'archive hash mismatch'):
                source_io.fetch_archive(REPO_NAME, COMMIT, temporary, expected)

    def test_incompatible_skill_scoped_license_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = write_archive(temporary, {
                'LICENSE': MIT,
                'skills/example/SKILL.md': b'A research workflow with source evidence and outputs.',
                'skills/example/LICENSE': b'Creative Commons Attribution-NonCommercial 4.0',
            })
            snapshot = source_io.Snapshot(path)
            root_path, root_id = source_io.root_license(snapshot)
            self.assertEqual((root_path, root_id), ('LICENSE', 'MIT'))
            scoped_path, retained = source_io.applicable_licenses(
                snapshot, 'skills/example/SKILL.md', root_path)
            self.assertEqual(scoped_path, 'skills/example/LICENSE')
            self.assertIn(root_path, retained)
            with self.assertRaisesRegex(ValueError, 'No supported explicit'):
                source_io.license_id(snapshot.read(scoped_path))
            snapshot.archive.close()


class MetadataBoundaryTests(unittest.TestCase):
    def valid_metadata(self):
        metadata = {'include': True, 'category': 'research'}
        for field in update_catalog.TEXT_FIELDS:
            metadata[field] = '有效的中文研究说明'
            metadata[field + 'En'] = 'A valid English research description'
        for field in update_catalog.ARRAY_FIELDS:
            metadata[field] = ['输入信息']
            metadata[field + 'En'] = ['source inputs']
        metadata['evidenceQuotes'] = [
            'The first exact source quotation.',
            'A second exact source quotation.',
        ]
        return metadata

    def test_valid_bilingual_metadata_and_exact_quotes_are_accepted(self):
        original = ('The first exact source quotation. A second exact source quotation. '
                    'Additional original source text.')
        update_catalog.validate_metadata(self.valid_metadata(), original)

    def test_english_array_string_is_rejected(self):
        metadata = self.valid_metadata()
        metadata['inputsEn'] = 'source inputs'
        with self.assertRaisesRegex(ValueError, 'Invalid bilingual array'):
            update_catalog.validate_metadata(metadata, 'The first exact source quotation. A second exact source quotation.')

    def test_fabricated_evidence_quotes_are_rejected(self):
        metadata = self.valid_metadata()
        metadata['evidenceQuotes'] = [
            'A fabricated exact source quotation.',
            'Another fabricated source quotation.',
        ]
        original = 'The actual source has different wording throughout this document.'
        with self.assertRaisesRegex(ValueError, 'exact source quotations'):
            update_catalog.validate_metadata(metadata, original)


class WriteProtectionTests(unittest.TestCase):
    def test_existing_source_health_failure_does_not_mutate_write_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'dist/data').mkdir(parents=True)
            (root / 'dist/licenses').mkdir()
            (root / 'maintenance').mkdir()
            catalog_path = root / 'dist/data/catalog.json'
            license_path = root / 'dist/licenses/example-license.txt'
            ledger_path = root / 'maintenance/ledger.jsonl'
            policy_path = root / 'maintenance/sources.json'
            catalog_path.write_text(json.dumps({
                'sources': [{
                    'repository': 'https://github.com/' + REPO_NAME,
                    'commit': COMMIT,
                    'archive': source_io.archive_name(REPO_NAME, COMMIT),
                    'archiveSha256': 'b' * 64,
                }],
                'skills': [],
            }))
            license_path.write_bytes(MIT)
            ledger_path.write_text('{"prior":"receipt"}\n')
            policy_path.write_text(json.dumps({'tracked': [], 'candidates': []}))
            originals = {
                catalog_path: catalog_path.read_bytes(),
                license_path: license_path.read_bytes(),
                ledger_path: ledger_path.read_bytes(),
            }
            args = SimpleNamespace(
                archive_dir=str(root / '.cache/sources'),
                no_discovery=True,
                max_items=3,
                write=True,
            )
            receipt = {'runAt': 'test-only'}
            with mock.patch.object(update_catalog, 'ROOT', root), mock.patch.object(
                    update_catalog, 'fetch_archive', side_effect=ValueError('pinned archive hash mismatch')) as fetch:
                with self.assertRaisesRegex(ValueError, 'pinned archive hash mismatch'):
                    update_catalog.run(args, receipt)
            fetch.assert_called_once()
            self.assertEqual(receipt, {'runAt': 'test-only'})
            for path, content in originals.items():
                self.assertEqual(path.read_bytes(), content)


if __name__ == '__main__':
    unittest.main()

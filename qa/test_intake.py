"""Boundary tests for the bounded AlphaKit intake path."""
import hashlib
import json
import shutil
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


def valid_metadata():
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
    valid_metadata = staticmethod(valid_metadata)

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

    def test_invalid_fields_report_presence_type_and_length(self):
        metadata = self.valid_metadata()
        metadata['summary'] = None
        with self.assertRaises(ValueError) as raised:
            update_catalog.validate_metadata(metadata, 'The first exact source quotation. A second exact source quotation.')
        self.assertEqual(raised.exception.diagnostic, {
            'field': 'summary', 'exists': True, 'type': 'NoneType', 'length': None})

    def test_dependencies_en_shape_boundaries_are_described(self):
        original = ('The first exact source quotation. A second exact source quotation. '
                    'Additional original source text.')
        cases = [
            ('missing', None, False, 'NoneType', None),
            ('null', None, True, 'NoneType', None),
            ('string', 'shell', True, 'str', 5),
            ('mapping', {}, True, 'dict', 0),
            ('empty-array', [], True, 'list', 0),
            ('long-array', ['dependency'] * 13, True, 'list', 13),
        ]
        for label, value, expected_exists, expected_type, expected_length in cases:
            with self.subTest(case=label):
                metadata = self.valid_metadata()
                if label == 'missing':
                    metadata.pop('dependenciesEn', None)
                else:
                    metadata['dependenciesEn'] = value
                with self.assertRaises(ValueError) as raised:
                    update_catalog.validate_metadata(metadata, original)
                details = getattr(raised.exception, 'diagnostic', {})
                self.assertEqual(details.get('exists'), expected_exists)
                self.assertEqual(details.get('field'), 'dependenciesEn')
                self.assertEqual(details.get('type'), expected_type)
                self.assertEqual(details.get('length'), expected_length)

    def test_correct_dependencies_en_array_passes_existing_validation(self):
        original = ('The first exact source quotation. A second exact source quotation. '
                    'Additional original source text.')
        metadata = self.valid_metadata()
        metadata['dependenciesEn'] = ['Python', 'pandas']
        update_catalog.validate_metadata(metadata, original)

    def test_nonlinear_and_language_failures_report_actual_fields(self):
        original = ('The first exact source quotation. A second exact source quotation. '
                    'Additional original source text.')
        cases = [
            ('include', False,
             {'field': 'include', 'exists': True, 'type': 'bool', 'length': None}),
            ('summaryEn', '这是中文说明',
             {'field': 'summaryEn', 'exists': True, 'type': 'str', 'length': 6}),
            ('dependenciesEn', ['中文依赖'],
             {'field': 'dependenciesEn', 'exists': True, 'type': 'list', 'length': 1}),
            ('category', 'unknown',
             {'field': 'category', 'exists': True, 'type': 'str', 'length': 7}),
            ('category', [],
             {'field': 'category', 'exists': True, 'type': 'list', 'length': 0}),
            ('category', {},
             {'field': 'category', 'exists': True, 'type': 'dict', 'length': 0}),
            ('evidenceQuotes', [['unhashable'], 'The first exact source quotation.'],
             {'field': 'evidenceQuotes', 'exists': True, 'type': 'list', 'length': 2}),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field):
                metadata = self.valid_metadata()
                metadata[field] = value
                before = dict(metadata)
                with self.assertRaises(ValueError) as raised:
                    update_catalog.validate_metadata(metadata, original)
                self.assertEqual(raised.exception.diagnostic, expected)
                self.assertEqual(metadata, before)


class CurateDiagnosticsTests(unittest.TestCase):
    original = ('The first exact source quotation. A second exact source quotation. '
                'Additional original source text supplies enough source material for this review boundary, deterministic source checks and repeatable offline QA evidence.')

    def responses(self, initial, repaired, approved=True):
        def responder(messages, max_tokens=5500):
            if max_tokens == 900:
                return {'approve': approved, 'reason': 'test review'}
            if len(messages) == 2:
                return initial
            if len(messages) == 4:
                return repaired
            raise AssertionError('Unexpected model call')
        return responder

    def test_repair_success_is_independently_reviewed(self):
        initial = dict(valid_metadata(), dependenciesEn='shell')
        repaired = dict(valid_metadata(), dependenciesEn=['Python', 'pandas'])
        with mock.patch.object(update_catalog, 'model_json',
                               side_effect=self.responses(initial, repaired)) as model_json:
            metadata, reason, diagnostics = update_catalog.curate(
                REPO_NAME, 'skills/example/SKILL.md', self.original)
        self.assertEqual(metadata, repaired)
        self.assertIn('deterministic', reason)
        self.assertEqual(model_json.call_count, 3)
        self.assertEqual([item['stage'] for item in diagnostics], ['initial'])
        self.assertEqual(diagnostics[0]['field'], 'dependenciesEn')

    def test_independent_review_rejection_keeps_earlier_diagnostic(self):
        initial = dict(valid_metadata(), dependenciesEn=None)
        repaired = dict(valid_metadata(), dependenciesEn=['Python'])
        with mock.patch.object(update_catalog, 'model_json',
                               side_effect=self.responses(initial, repaired, approved=False)):
            metadata, reason, diagnostics = update_catalog.curate(
                REPO_NAME, 'skills/example/SKILL.md', self.original)
        self.assertIsNone(metadata)
        self.assertEqual(reason, 'Independent model review rejected candidate')
        self.assertEqual([item['stage'] for item in diagnostics], ['initial'])
        self.assertEqual(diagnostics[0]['length'], None)

    def test_repair_failure_returns_candidate_rejection_with_stages(self):
        initial = dict(valid_metadata(), name=None)
        repaired = dict(valid_metadata(), dependenciesEn=[])
        with mock.patch.object(update_catalog, 'model_json',
                               side_effect=self.responses(initial, repaired)):
            metadata, reason, diagnostics = update_catalog.curate(
                REPO_NAME, 'skills/example/SKILL.md', self.original)
        self.assertIsNone(metadata)
        self.assertEqual(reason, 'Candidate metadata failed format validation after one repair')
        self.assertEqual([(item['stage'], item['field']) for item in diagnostics],
                         [('initial', 'name'), ('repair', 'dependenciesEn')])
        self.assertEqual([item['reason'] for item in diagnostics],
                         ['Invalid bilingual text field: name',
                          'Invalid bilingual array field: dependenciesEn'])


    def test_model_transport_and_authentication_failures_propagate(self):
        invalid = dict(valid_metadata(), dependenciesEn='shell')
        failure = RuntimeError('synthetic network or authentication failure')
        stages = {
            'initial': [failure],
            'repair': [invalid, failure],
            'independent_review': [valid_metadata(), failure],
        }
        for stage, responses in stages.items():
            with self.subTest(stage=stage):
                with mock.patch.object(update_catalog, 'model_json', side_effect=responses):
                    with self.assertRaises(RuntimeError) as raised:
                        update_catalog.curate(
                            REPO_NAME, 'skills/example/SKILL.md', self.original)
                self.assertIs(raised.exception, failure)


class CatalogRunTests(unittest.TestCase):
    original_text = ('The first exact source quotation. A second exact source quotation. '
                     'Additional original source text supplies enough source material for this review boundary, deterministic source checks and repeatable offline QA evidence.')
    synthetic_text = ('The first exact source quotation. A second exact source quotation. '
                      + ('Synthetic offline workflow evidence. ' * 12))
    new_text = synthetic_text + ' The changed source remains eligible for deterministic hash checks.'

    def build_root(self, root, commit=COMMIT, text=original_text):
        dist = root / 'dist'
        maintenance = root / 'maintenance'
        cache = root / '.cache/sources'
        stage = root / 'staging'
        (root / 'qa').mkdir()
        shutil.copy2(REPO / 'qa/verify-catalog.py', root / 'qa/verify-catalog.py')
        for directory in (dist / 'data', dist / 'licenses', maintenance,
                          cache, stage / 'dist'):
            directory.mkdir(parents=True, exist_ok=True)
        archive = write_archive(cache, {
            'LICENSE': MIT,
            'skills/example/SKILL.md': text.encode(),
        }, commit=commit)
        archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
        (dist / 'licenses/example-license.txt').write_bytes(MIT)
        license_name = REPO_NAME.replace('/', '--') + '--LICENSE'
        (dist / 'licenses' / license_name).write_bytes(MIT)
        (maintenance / 'sources.json').write_text(json.dumps({
            'tracked': [{'repository': REPO_NAME, 'prefix': ''}], 'candidates': []}))
        (maintenance / 'ledger.jsonl').write_text('')
        return archive_hash

    def catalog(self, root, archive_hash, commit=COMMIT):
        dist = root / 'dist'
        maintenance = root / 'maintenance'
        cache = root / '.cache/sources'
        stage = root / 'staging'
        snapshot = source_io.Snapshot(cache / source_io.archive_name(REPO_NAME, commit))
        entry = update_catalog.make_entry(REPO_NAME, commit, 'skills/example/SKILL.md',
                                          valid_metadata(), 'MIT', 'LICENSE')
        record = update_catalog.source_record(REPO_NAME, commit, snapshot, [entry], archive_hash,
                                              None, stage)
        return {'sources': [record], 'skills': [entry]}

    def args(self, root):
        cache = root / '.cache/sources'
        return SimpleNamespace(archive_dir=str(cache), no_discovery=True,
                               max_items=3, write=True)

    def configure_updates(self, root, new_commit, new_text):
        cache = root / '.cache/sources'
        new_archive = write_archive(cache, {
            'LICENSE': MIT,
            'skills/example/SKILL.md': new_text.encode(),
        }, commit=new_commit)
        return hashlib.sha256(new_archive.read_bytes()).hexdigest()

    def responses(self, initial, repaired):
        def responder(messages, max_tokens=5500):
            if len(messages) == 2:
                return initial
            if len(messages) == 4:
                return repaired
            if max_tokens == 900:
                return {'approve': True, 'reason': 'test review'}
            raise AssertionError('Unexpected model call')
        return responder

    def test_repair_failure_holds_existing_source_and_preserves_pin(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        dist = root / 'dist'
        maintenance = root / 'maintenance'
        cache = root / '.cache/sources'
        old_hash = self.build_root(root)
        old_catalog = self.catalog(root, old_hash)
        old_entry = old_catalog['skills'][0]
        old_source = old_catalog['sources'][0]
        (dist / 'data/catalog.json').write_text(json.dumps(old_catalog))
        new_commit = 'b' * 40
        self.configure_updates(root, new_commit, self.new_text)
        initial = dict(valid_metadata(), dependenciesEn=[])
        repaired = dict(valid_metadata(), dependenciesEn={'shell': True})
        def latest_commit(repo):
            self.assertEqual(repo, REPO_NAME)
            return new_commit
        args = self.args(root)
        receipt = {'runAt': 'test-only'}
        with mock.patch.object(update_catalog, 'ROOT', root), mock.patch.object(
                update_catalog, 'latest_commit', side_effect=latest_commit), mock.patch.object(
                update_catalog, 'model_json', side_effect=self.responses(initial, repaired)):
            update_catalog.run(args, receipt)
        written = json.loads((dist / 'data/catalog.json').read_text())
        self.assertEqual(receipt['status'], 'succeeded')
        self.assertEqual(receipt['refreshed'], 0)
        rejection = receipt['rejected'][0]
        self.assertEqual({key: value for key, value in rejection.items() if key != 'diagnostics'}, {
            'repository': REPO_NAME,
            'commit': new_commit,
            'path': 'skills/example/SKILL.md',
            'contentHash': hashlib.sha256(self.new_text.encode()).hexdigest(),
            'reason': 'Candidate metadata failed format validation after one repair',
        })
        self.assertEqual(receipt['sources'], [{
            'repository': REPO_NAME, 'status': 'held', 'commit': COMMIT}])
        self.assertEqual(len(receipt['skipped']), 1)
        self.assertEqual(receipt['skipped'][0]['field'], 'dependenciesEn')
        self.assertEqual(receipt['skipped'][0]['path'], 'skills/example/SKILL.md')
        self.assertTrue(receipt['skipped'][0]['id'].startswith('skill-'))
        status = json.loads((dist / 'data/update-status.json').read_text())
        self.assertEqual(status['skipped'], 1)
        self.assertEqual([(item['stage'], item['field'], item['type'], item['length'])
                          for item in rejection['diagnostics']],
                         [('initial', 'dependenciesEn', 'list', 0),
                          ('repair', 'dependenciesEn', 'dict', 1)])
        self.assertEqual(written['skills'], [old_entry])
        self.assertEqual(written['sources'], [old_source])
        self.assertEqual((dist / 'licenses/example-license.txt').read_bytes(), MIT)

    def test_bad_new_candidate_is_isolated_and_valid_candidate_is_added(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        dist = root / 'dist'
        maintenance = root / 'maintenance'
        cache = root / '.cache/sources'
        archive_hash = self.build_root(root)
        catalog = self.catalog(root, archive_hash)
        (dist / 'data/catalog.json').write_text(json.dumps(catalog))
        (maintenance / 'sources.json').write_text(json.dumps({
            'tracked': [{'repository': REPO_NAME, 'prefix': ''}],
            'candidates': ['example/new-skills']}))
        new_commit = 'c' * 40
        bad_text = self.synthetic_text + ' The invalid candidate has a deliberately malformed dependency.'
        good_text = self.synthetic_text + ' The valid candidate uses a supported dependency array.'
        write_archive(cache, {
            'LICENSE': MIT,
            'skills/example/SKILL.md': bad_text.encode(),
            'skills/valid/SKILL.md': good_text.encode(),
        }, repo='example/new-skills', commit=new_commit)
        self.assertEqual(len({hashlib.sha256(text.encode()).hexdigest() for text in
                              (self.original_text, bad_text, good_text)}), 3)
        bad = dict(valid_metadata(), dependenciesEn={'shell': True})
        good = dict(valid_metadata(), dependenciesEn=['Python', 'pandas'])
        def responder(messages, max_tokens=5500):
            if max_tokens == 900:
                return {'approve': True, 'reason': 'test review'}
            evidence = json.loads(messages[1]['content'])
            expected = bad if evidence['path'] == 'skills/example/SKILL.md' else good
            return expected
        args = self.args(root)
        receipt = {'runAt': 'test-only'}
        with mock.patch.object(update_catalog, 'ROOT', root), mock.patch.object(
                update_catalog, 'latest_commit', side_effect=lambda repo: (
                    COMMIT if repo == REPO_NAME else new_commit)), mock.patch.object(
                update_catalog, 'model_json', side_effect=responder):
            update_catalog.run(args, receipt)
        written = json.loads((dist / 'data/catalog.json').read_text())
        self.assertEqual(receipt['status'], 'succeeded')
        self.assertEqual(receipt['added'], 1)
        self.assertEqual(receipt['reviewed'], 2)
        self.assertEqual(len(written['skills']), 2)
        self.assertEqual(written['skills'][-1]['sourcePath'], 'skills/valid/SKILL.md')
        self.assertEqual(receipt['rejected'][0]['repository'], 'example/new-skills')
        self.assertEqual(receipt['rejected'][0]['commit'], new_commit)
        self.assertEqual(receipt['rejected'][0]['path'], 'skills/example/SKILL.md')
        self.assertEqual(receipt['rejected'][0]['contentHash'],
                         hashlib.sha256(bad_text.encode()).hexdigest())
        self.assertEqual([(item['stage'], item['field']) for item in receipt['rejected'][0]['diagnostics']],
                         [('initial', 'dependenciesEn'), ('repair', 'dependenciesEn')])
        self.assertEqual(receipt['rejected'][0]['diagnostics'][1]['type'], 'dict')
        self.assertEqual(receipt['rejected'][0]['diagnostics'][1]['length'], 1)
        self.assertEqual(receipt['sourceFailures'], [])
        self.assertEqual(receipt['sources'][-1]['status'], 'verified')
        self.assertEqual([(item['repository'], item['path'], item['field']) for item in receipt['skipped']],
                         [('example/new-skills', 'skills/example/SKILL.md', 'dependenciesEn')])


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

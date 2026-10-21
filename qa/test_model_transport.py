"""Offline transport-boundary tests for the model call wrapper."""
import contextlib
import email.utils
import io
import json
import os
import socket
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))

import update_catalog


class _Response:
    def __init__(self, payload, headers=None):
        self._body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.headers = headers or {}

    def read(self, limit=-1):
        return self._body[:limit] if limit >= 0 else self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def http_error(status, payload=b'', headers=None):
    message_headers = email.message.Message()
    for name, value in (headers or {}).items():
        message_headers[name] = value
    return urllib.error.HTTPError(
        update_catalog.ENDPOINT, status, 'synthetic HTTP failure', message_headers, io.BytesIO(payload))


def success_payload(content='{"ok":true}', model=update_catalog.MODEL):
    return {'model': model, 'usage': {'total_tokens': 11},
            'choices': [{'message': {'content': content}}]}


def error_body(code, message='restricted provider detail'):
    return json.dumps({'error': {'code': code, 'message': message}}).encode()


@contextlib.contextmanager
def local_timezone(name):
    previous = os.environ.get('TZ')
    os.environ['TZ'] = name
    time.tzset()
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = previous
        time.tzset()


class TransportTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.model_calls = []
        patchers = [
            mock.patch.dict(os.environ, {'ZHIPU_API_KEY': 'synthetic-offline-key'}),
            mock.patch.object(update_catalog, 'MODEL_CALLS', self.model_calls),
            mock.patch.object(update_catalog.time, 'sleep'),
            mock.patch.object(update_catalog.random, 'uniform', return_value=0),
            mock.patch.object(socket, 'socket', side_effect=AssertionError('offline network guard')),
        ]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def call_model(self):
        return update_catalog.model_json([{'role': 'user', 'content': 'offline evidence'}])

    def assert_diagnostic(self, exception, attempts, provider_code, decisions):
        self.assertEqual(exception.diagnostic, {
            'httpStatus': 429, 'providerCode': provider_code,
            'attempts': attempts, 'decisions': decisions,
        })

    def test_transient_429_1302_retries_then_records_existing_success(self):
        responses = [
            http_error(429, error_body(1302), {'Retry-After': '1'}),
            _Response(success_payload()),
        ]
        with mock.patch.object(update_catalog.urllib.request, 'urlopen', side_effect=responses):
            self.assertEqual(self.call_model(), {'ok': True})
        self.assertEqual(self.model_calls, [{'model': update_catalog.MODEL,
                                             'usage': {'total_tokens': 11}}])
        update_catalog.time.sleep.assert_called_once_with(1)

    def test_retryable_429_stops_after_four_attempts(self):
        with mock.patch.object(update_catalog.urllib.request, 'urlopen',
                               side_effect=[http_error(429, error_body(1305))
                                            for _ in range(4)]) as urlopen:
            with self.assertRaises(update_catalog.ModelTransportError) as raised:
                self.call_model()
        self.assertEqual(raised.exception.diagnostic['httpStatus'], 429)
        self.assertEqual(raised.exception.diagnostic['providerCode'], 1305)
        self.assertEqual(raised.exception.diagnostic['attempts'], 4)
        self.assertEqual([decision['retry'] for decision in
                          raised.exception.diagnostic['decisions']], [True, True, True, False])
        self.assertEqual(urlopen.call_count, 4)
        self.assertEqual(update_catalog.time.sleep.call_args_list,
                         [mock.call(5.0), mock.call(10.0), mock.call(20.0)])

    def test_numeric_string_transient_code_retries_then_succeeds(self):
        result = None
        with mock.patch.object(update_catalog.urllib.request, 'urlopen', side_effect=[
                http_error(429, error_body('1302')), _Response(success_payload())]) as urlopen:
            try:
                result = self.call_model()
            except RuntimeError:
                pass
        self.assertEqual(urlopen.call_count, 2, 'numeric string 1302 must retain its transient meaning')
        self.assertEqual(result, {'ok': True})

    def test_permanent_and_unknown_429_codes_do_not_retry(self):
        cases = [1113, 1308, 1309, 1310, 1311, 1313, 1314, 1315, 1316, 1317,
                 1318, 1319, 1320, 1321, 9999]
        for code in cases:
            with self.subTest(code=code):
                with mock.patch.object(update_catalog.urllib.request, 'urlopen',
                                       side_effect=http_error(429, error_body(code))) as urlopen:
                    with self.assertRaises(update_catalog.ModelTransportError) as raised:
                        self.call_model()
                self.assertEqual(urlopen.call_count, 1)
                update_catalog.time.sleep.assert_not_called()
                self.assertEqual(raised.exception.diagnostic['attempts'], 1)
                self.assertEqual(raised.exception.diagnostic['providerCode'], code)

    def test_valid_integer_retry_after_is_honored(self):
        with mock.patch.object(update_catalog.urllib.request, 'urlopen',
                               side_effect=[http_error(429, error_body(1302),
                                                        {'Retry-After': '7'}), _Response(success_payload())]):
            self.call_model()
        update_catalog.time.sleep.assert_called_once_with(7)

    def check_http_date_retry_after(self, timezone_name):
        now = 1_700_000_000.75
        retry_at = 1_700_000_009
        headers = {'Retry-After': email.utils.formatdate(retry_at, usegmt=True)}
        with local_timezone(timezone_name), mock.patch.object(update_catalog.time, 'time', return_value=now):
            with mock.patch.object(update_catalog.urllib.request, 'urlopen',
                                   side_effect=[http_error(429, error_body(1302), headers),
                                                _Response(success_payload())]):
                self.call_model()
        self.assertEqual(update_catalog.time.sleep.call_count, 1)
        self.assertGreaterEqual(update_catalog.time.sleep.call_args.args[0], 8.25,
                                'Retry-After HTTP-date must never cause an early retry')

    def test_valid_http_date_retry_after_is_honored(self):
        self.check_http_date_retry_after('UTC')

    def test_valid_http_date_is_independent_of_local_timezone(self):
        self.check_http_date_retry_after('Asia/Shanghai')

    def test_retry_wait_budget_is_cumulative(self):
        failure = None
        with mock.patch.object(update_catalog.urllib.request, 'urlopen', side_effect=[
                http_error(429, error_body(1302), {'Retry-After': '40'}),
                http_error(429, error_body(1302), {'Retry-After': '40'}),
                _Response(success_payload())]) as urlopen:
            try:
                self.call_model()
            except RuntimeError as error:
                failure = error
        self.assertLessEqual(sum(call.args[0] for call in update_catalog.time.sleep.call_args_list), 60,
                             'Retry budget applies to the total wait, not each delay')
        self.assertEqual(urlopen.call_count, 2)
        self.assertIsInstance(failure, update_catalog.ModelTransportError)
        self.assertEqual(failure.diagnostic['attempts'], 2)
        self.assertEqual(failure.diagnostic['decisions'], [
            {'httpStatus': 429, 'providerCode': 1302, 'retry': True, 'waitSeconds': 40},
            {'httpStatus': 429, 'providerCode': 1302, 'retry': False, 'waitSeconds': 40},
        ])

    def test_retry_after_over_total_budget_defers_without_retry(self):
        headers = {'Retry-After': '61'}
        with mock.patch.object(update_catalog.urllib.request, 'urlopen',
                               side_effect=http_error(429, error_body(1302), headers)) as urlopen:
            with self.assertRaises(update_catalog.ModelTransportError) as raised:
                self.call_model()
        self.assertEqual(urlopen.call_count, 1)
        update_catalog.time.sleep.assert_not_called()
        self.assertEqual(raised.exception.diagnostic['decisions'],
                         [{'httpStatus': 429, 'providerCode': 1302,
                           'retry': False, 'waitSeconds': 61}])

    def test_malformed_oversized_and_message_bearing_errors_are_sanitized(self):
        marker = 'provider-secret-marker'
        prefix = error_body(1302, marker)
        oversized = prefix + b' ' * (update_catalog.MAX_HTTP_BODY_BYTES - len(prefix)) + b'x'
        cases = [b'not-json', error_body(True, marker),
                 error_body('not-a-code', marker), error_body(1309, marker), oversized]
        for payload in cases:
            with self.subTest(payload_length=len(payload)):
                failure = None
                with mock.patch.object(update_catalog.urllib.request, 'urlopen', side_effect=[
                        http_error(429, payload), _Response(success_payload())]) as urlopen:
                    try:
                        self.call_model()
                    except RuntimeError as error:
                        failure = error
                self.assertEqual(urlopen.call_count, 1)
                self.assertIsInstance(failure, update_catalog.ModelTransportError)
                self.assertNotIn(marker, str(failure))
                self.assertNotIn(marker, repr(failure))
                self.assertNotIn(marker, json.dumps(failure.diagnostic))
                self.assertNotIn('restricted provider detail', json.dumps(failure.diagnostic))

    def test_non_429_timeout_network_invalid_success_and_wrong_model_do_not_retry(self):
        payload = success_payload(model='wrong-model')
        cases = [
            ('http-500', http_error(500, b'failed'), RuntimeError),
            ('timeout', TimeoutError('offline timeout'), RuntimeError),
            ('network', urllib.error.URLError('offline failure'), RuntimeError),
            ('invalid-json', _Response(b'{bad json'), ValueError),
            ('wrong-model', _Response(payload), ValueError),
        ]
        for name, response, exception_type in cases:
            with self.subTest(name=name):
                with mock.patch.object(update_catalog.urllib.request, 'urlopen',
                                       side_effect=[response]) as urlopen:
                    with self.assertRaises(exception_type):
                        self.call_model()
                self.assertEqual(urlopen.call_count, 1)
                self.assertEqual(self.model_calls, [])

    def test_main_failure_receipt_is_safe_and_write_targets_are_unchanged(self):
        diagnostic = {'httpStatus': 429, 'providerCode': 1302, 'attempts': 3, 'decisions': []}
        failure = update_catalog.ModelTransportError(diagnostic)
        with tempfile.TemporaryDirectory(prefix='alphakit-transport-test-') as temporary:
            fixture_root = Path(temporary)
            receipt_path = fixture_root / 'receipt.json'
            sentinels = {}
            for relative in ('dist/data/catalog.json', 'dist/data/update-status.json',
                             'dist/licenses/offline-license.txt', 'maintenance/ledger.jsonl'):
                path = fixture_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic sentinel\n')
                sentinels[path] = path.read_bytes()
            with mock.patch.object(update_catalog, 'run', side_effect=failure), mock.patch.object(
                    sys, 'argv', ['update_catalog.py', '--receipt', str(receipt_path)]), mock.patch.dict(
                    os.environ, {'ZHIPU_API_KEY': 'synthetic-offline-key'}):
                with self.assertRaises(SystemExit) as raised:
                    update_catalog.main()
            receipt = json.loads(receipt_path.read_text())
            self.assertEqual(raised.exception.code, 1)
            self.assertEqual(receipt['status'], 'failed')
            self.assertEqual(receipt['modelFailure'], diagnostic)
            self.assertEqual(receipt['modelCalls'], [])
            for path, content in sentinels.items():
                self.assertEqual(path.read_bytes(), content)

    def test_socket_is_guarded(self):
        with self.assertRaisesRegex(AssertionError, 'offline network guard'):
            socket.socket()


if __name__ == '__main__':
    unittest.main()

import unittest
from privacy_preflight import content_hits, identity_hits

class PrivacyTests(unittest.TestCase):
    def test_private_contact_rejected_without_echo(self):
        email = 'synthetic-person' + '@example.invalid'
        raw = 'author Synthetic <' + email + '> 0 +0000\ncommitter Synthetic <' + email + '> 0 +0000\n'
        result = identity_hits(raw)
        self.assertEqual(len(result), 2)
        self.assertNotIn(email, str(result))

    def test_github_private_identities_allowed(self):
        raw = 'author Bot <1+bot@users.noreply.github.com> 0 +0000\ncommitter GitHub <noreply@noreply.github.com> 0 +0000\n'
        self.assertEqual(identity_hits(raw), [])

    def test_token_and_private_path_blocked(self):
        token = 'ghp_' + 'A' * 36
        self.assertIn('credential-token', content_hits(token.encode()))
        self.assertIn('personal-path', content_hits(('/Users/' + 'synthetic/private').encode()))

    def test_allowed_public_code(self):
        self.assertEqual(content_hits(b'const endpoint="http://127.0.0.1:5188"; process.env.API_KEY'), [])

    def test_binary_requires_review(self):
        self.assertEqual(content_hits(b'\xff\xfe'), ['binary-requires-manual-review'])

    def test_coauthor_contact_is_blocked_without_echo(self):
        email = 'synthetic-coauthor' + '@example.invalid'
        raw = 'author Bot <1+bot@users.noreply.github.com> 0 +0000\ncommitter Bot <1+bot@users.noreply.github.com> 0 +0000\n\nCo-authored-by: Synthetic <' + email + '>\n'
        result = identity_hits(raw)
        self.assertIn('commit-message-contact-email', result)
        self.assertNotIn(email, str(result))

if __name__ == '__main__':
    unittest.main()

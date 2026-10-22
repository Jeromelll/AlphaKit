import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name('privacy_pre_push.py').resolve()

class HookIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = dict(os.environ)
        for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
            self.env.pop(k, None)
        self.env.update(GIT_AUTHOR_NAME='Synthetic', GIT_COMMITTER_NAME='Synthetic',
                        GIT_AUTHOR_EMAIL='1+synthetic@users.noreply.github.com',
                        GIT_COMMITTER_EMAIL='1+synthetic@users.noreply.github.com')
        self.git('init', '-q')
        (self.root / 'safe.txt').write_text('public fixture\n')
        self.base = self.commit()
        self.git('update-ref', 'refs/remotes/origin/main', self.base)

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, env=self.env, stderr=subprocess.DEVNULL).decode().strip()

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic fixture')
        return self.git('rev-parse', 'HEAD')

    def hook(self, head, remote=None, ref='refs/heads/main'):
        data = f'refs/heads/test {head} {ref} {remote or self.base}\n'
        return subprocess.run([sys.executable, str(HOOK)], cwd=self.root, env=self.env, input=data, text=True, capture_output=True)

    def test_clean_normal_and_new_branch(self):
        (self.root / 'safe.txt').write_text('another public fixture\n')
        head = self.commit()
        self.assertEqual(self.hook(head).returncode, 0)
        self.assertEqual(self.hook(head, '0' * 40, 'refs/heads/new').returncode, 0)

    def test_contact_blocked_without_echo(self):
        email = 'synthetic-private' + '@example.invalid'
        self.env['GIT_AUTHOR_EMAIL'] = email
        (self.root / 'safe.txt').write_text('changed\n')
        result = self.hook(self.commit())
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(email, result.stdout + result.stderr)

    def test_deleted_intermediate_secret_still_blocked(self):
        p = self.root / 'temporary.txt'
        token = 'ghp_' + 'Z' * 36
        p.write_text(token)
        self.commit()
        p.unlink()
        result = self.hook(self.commit())
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(token, result.stdout + result.stderr)

    def test_missing_remote_baseline_blocks(self):
        result = self.hook(self.base, 'f' * 40)
        self.assertNotEqual(result.returncode, 0)

    def test_tag_requires_review(self):
        self.assertNotEqual(self.hook(self.base, ref='refs/tags/v1').returncode, 0)

if __name__ == '__main__':
    unittest.main()

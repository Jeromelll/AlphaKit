"""Git pre-push entrypoint: check every ref before any is sent."""
import subprocess
import sys
from pathlib import Path

ZERO = '0' * 40

def main():
    checker = Path(__file__).with_name('privacy_preflight.py')
    for line in sys.stdin:
        parts = line.split()
        if len(parts) != 4:
            print('Privacy check: invalid hook input', file=sys.stderr)
            return 1
        local_ref, local_sha, remote_ref, remote_sha = parts
        if local_sha == ZERO:
            continue
        if not remote_ref.startswith('refs/heads/'):
            print('Privacy check: non-branch ref requires manual review', file=sys.stderr)
            return 1
        if remote_sha == ZERO:
            try:
                base = subprocess.check_output(['git', 'rev-parse', '--verify', 'refs/remotes/origin/main^{commit}'], stderr=subprocess.DEVNULL).decode().strip()
            except subprocess.CalledProcessError:
                print('Privacy check: published main baseline unavailable', file=sys.stderr)
                return 1
        else:
            base = remote_sha
        try:
            subprocess.run(['git', 'cat-file', '-e', base + '^{commit}'], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'merge-base', '--is-ancestor', base, local_sha], check=True)
        except subprocess.CalledProcessError:
            print('Privacy check: missing baseline or non-fast-forward update requires review', file=sys.stderr)
            return 1
        result = subprocess.run([sys.executable, str(checker), '--range', base + '..' + local_sha])
        if result.returncode:
            return result.returncode
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

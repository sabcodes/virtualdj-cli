#!/usr/bin/env python3
"""Install only our new bridge bundle; existing bundles require an explicit, verified update."""
import argparse
from pathlib import Path
import plistlib
import time
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-owned', action='store_true', help='back up and update our identified bridge only')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        raise SystemExit('This prototype supports macOS only.')
    arch = 'arm64' if platform.machine() == 'arm64' else 'x86_64'
    built = subprocess.check_output([sys.executable, str(ROOT / 'tools/build.py'), '--arch', arch], text=True)
    source = Path(built.strip())
    folder = 'PluginsMacArm' if arch == 'arm64' else 'Plugins64'
    home = Path.home() / 'Library/Application Support/VirtualDJ'
    if not home.is_dir():
        raise SystemExit('VirtualDJ user directory not found; install path must be verified first.')
    target = home / folder / 'SoundEffect/AgentCLIBridge.bundle'
    backup = None
    if target.exists() or target.is_symlink():
        if not args.update_owned or target.is_symlink():
            raise SystemExit(f'Not overwriting an existing plugin: {target}')
        info = plistlib.loads((target / 'Contents/Info.plist').read_bytes())
        if info.get('CFBundleIdentifier') != 'com.sabcodes.vdj-cli.bridge':
            raise SystemExit('Refusing to replace a plugin not identified as our bridge.')
        backup = Path.home() / f'Library/Caches/virtualdj-cli/install-backups/{time.time_ns()}/AgentCLIBridge.bundle'
        backup.parent.mkdir(parents=True, exist_ok=True)
        target.rename(backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(source, target)
        subprocess.run(['xattr', '-cr', str(target)], check=True)
        subprocess.run(['codesign', '--verify', '--strict', str(target)], check=True)
    except Exception:
        if target.exists():
            shutil.rmtree(target)  # Only the new copy created by this install attempt.
        if backup:
            backup.rename(target)
        raise
    if backup:
        print(f'Previous bridge preserved at {backup}', file=sys.stderr)
    print(target)
    print('Open/reopen VirtualDJ manually; select Agent CLI Bridge from the master effects list, then run ./vdj doctor.')


if __name__ == '__main__':
    main()

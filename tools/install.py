#!/usr/bin/env python3
"""Install only our new bridge bundle; existing bundles are never overwritten."""
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
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
    if target.exists():
        raise SystemExit(f'Not overwriting an existing plugin: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    subprocess.run(['xattr', '-cr', str(target)], check=True)
    subprocess.run(['codesign', '--verify', '--strict', str(target)], check=True)
    print(target)
    print('Open/reopen VirtualDJ manually; select Agent CLI Bridge from the master effects list, then run ./vdj doctor.')


if __name__ == '__main__':
    main()

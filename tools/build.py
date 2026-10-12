#!/usr/bin/env python3
"""Build the macOS bundle against locally fetched, pinned official SDK headers."""
import argparse
import hashlib
from pathlib import Path
import plistlib
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SDK_URL = 'https://virtualdj.com/developers/VirtualDJ8_SDK_20211003.zip'
SDK_SHA256 = '77c23717509838f518d3176b088b97e8242ce357c2d78ce851d70386ae9f341e'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arch', choices=('arm64', 'x86_64'), default='arm64')
    args = parser.parse_args()
    sdk = ROOT / '.sdk'
    sdk.mkdir(exist_ok=True)
    archive = sdk / 'VirtualDJ8_SDK_20211003.zip'
    if not archive.exists():
        with urllib.request.urlopen(SDK_URL, timeout=30) as response:
            payload = response.read(1024 * 1024 + 1)
        if len(payload) > 1024 * 1024:
            raise RuntimeError('SDK download exceeds expected size')
        archive.write_bytes(payload)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SDK_SHA256:
        raise RuntimeError('SDK checksum mismatch; no headers extracted or build performed')
    with zipfile.ZipFile(archive) as package:
        (sdk / 'vdjPlugin8.h').write_bytes(package.read('vdjPlugin8.h'))
    # Build outside the synced workspace: file-provider metadata can invalidate code signing.
    bundle = Path.home() / 'Library/Caches/virtualdj-cli/build/AgentCLIBridge.bundle/Contents'
    (bundle / 'MacOS').mkdir(parents=True, exist_ok=True)
    subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-arch', args.arch,
                    '-bundle', '-framework', 'CoreFoundation', '-isystem', str(sdk),
                    str(ROOT / 'plugin/bridge.cpp'), '-o', str(bundle / 'MacOS/AgentCLIBridge')], check=True)
    with (bundle / 'Info.plist').open('wb') as output:
        plistlib.dump({'CFBundleExecutable': 'AgentCLIBridge', 'CFBundleIdentifier': 'com.sabcodes.vdj-cli.bridge',
                      'CFBundlePackageType': 'BNDL', 'CFBundleVersion': '1',
                      'CFBundleShortVersionString': '0.1.0'}, output)
    # Clear metadata only on our generated bundle before ad-hoc signing.
    subprocess.run(['xattr', '-cr', str(bundle.parent)], check=True)
    subprocess.run(['codesign', '--force', '--sign', '-', str(bundle.parent)], check=True)
    print(bundle.parent)


if __name__ == '__main__':
    main()

# VirtualDJ CLI

A macOS CLI for agents to operate the running VirtualDJ app through its plugin SDK, VDJScript and Automix. No desktop input automation. This tool works with local music files.

**Local-file milestone verified:** on the user’s VirtualDJ 2026 build 9644 (user reports Free), the CLI reads deck state, loads local files, controls playback, verifies BPM sync and completes no-sync crossfades. Live tests include Orion Sun — Mirage drums/vocals from the user's Stem Splitter output; app state and signal meter are verified, while subjective musical quality is unverified. Automix status/stop are live-tested; start/next retain harness coverage only.  The SDK license query is unavailable on the tested build and is reported as unknown.

## Setup

Requires Python 3 and Apple's existing command-line compiler tools. No Python packages are needed.

```bash
python3 tools/install.py
```

This downloads checksum-pinned SDK headers to ignored `.sdk/`, builds/signs our bundle in `~/Library/Caches/virtualdj-cli/build/`, and installs only a new bundle in the user's `SoundEffect` directory. Existing plugins are not overwritten by default. `python3 tools/install.py --update-owned` backs up and updates only a bundle identified as this bridge, with rollback if copy/signature verification fails. A running app retains its already-loaded plugin until the next manual restart; the CLI also handles the original 0.1.0 bridge’s positive execution results. SDK headers are not redistributed in Git.

Open/reopen VirtualDJ yourself. In the **master effects dropdown**, select **Agent CLI Bridge**. The Extensions settings page lists website plugins, so it is not the place to find this local plugin. Startup never plays music.

```bash
./vdj doctor
./vdj status
./vdj load --deck 2 '/absolute/path/to/song.wav'
./vdj play --deck 2
./vdj sync --deck 2 --to 1
./vdj transition --beats 8
./vdj automix start
./vdj automix next
./vdj automix stop
```

Use `./vdj --help` for the full command list. Output is JSON. Exit codes: 0 success, 1 operational failure, 2 invalid arguments.

Sync changes the target deck's playback BPM to the explicitly chosen source deck and verifies agreement within 0.05 BPM. Both decks must be loaded, Automix stopped and Pitch Lock off. It requests tempo matching without beat/phrase alignment or a playback change. VirtualDJ's elapsed-time readout accounts for tempo; use `get_position` or `get_time "elapsed" "absolute"` to compare file positions across pitch changes.

Load confirms the deck filepath and protects playing decks. Play/pause and Automix enable/disable confirm queried state. Transition, skip and raw script return submission only; they do not claim completion. Do not automatically retry a timed-out mutation. Status is sequential, not atomic. Playlist selection remains in VirtualDJ. Track loading accepts local audio files only.

The private native message port is scoped to the macOS user/session. The plugin executes SDK callbacks on the main run loop. Requests expire before dispatch; if execution already began, a transport timeout can leave an unknown outcome. Other programs in the same user/session can also address the port; this is a local trusted-user tool, not an isolated agent permission boundary.

## Verify

```bash
python3 tools/build.py
python3 -m unittest discover -s tests -v
```

The harness starts only our bridge with fake SDK callbacks. It tests real native IPC, Unicode metadata, guarded loading, transport/Automix state verification, malformed inputs, SDK rejection, expired requests and unavailable connections. It does not prove playback, DSP quality or Free license compatibility.

[Specification](docs/specs/2026-10-12-cli-bridge.md) · [Agent skill draft](skills/virtualdj-cli/SKILL.md) · [Initial discovery](docs/research/discovery.md)

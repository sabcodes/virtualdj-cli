# VirtualDJ CLI - context

Updated: 2026-10-18

VirtualDJ CLI lets agents control a running VirtualDJ instance on Apple Silicon macOS through terminal commands. The project supports **local music files only**. Track loading accepts filesystem paths; streaming-service URLs, URIs and account integrations are outside this tool's scope.

Repository: https://github.com/sabcodes/virtualdj-cli
Default branch: main

## Runtime

- `vdj`: Python standard library and ctypes client, JSON output.
- `plugin/bridge.cpp`: basic VirtualDJ SDK plugin, per-user/session Core Foundation message port, callbacks on the main run loop.
- The user opens VirtualDJ and selects AgentCLIBridge in the master effects dropdown.
- Agents operate through the CLI; no mouse or keyboard automation.
- `tools/build.py` and `tools/install.py` build/sign/install the owned plugin. SDK headers and build output stay ignored.

## Completed local-file milestone

As of 2026-10-12: doctor, deck status, protected loading, play/pause, explicit BPM sync, transitions, Automix controls and raw query/script access are implemented. Twelve native integration tests pass. Local loading, transport, BPM sync and no-sync crossfades were verified live on build 9644 with a user-reported Free installation; the user confirmed the setup works. Automix start/next have harness coverage only.

The reusable skill is `skills/virtualdj-cli/SKILL.md`; install it into the agent's skills directory and resolve the intended `vdj` executable. Use `--help` for current flags.

## Operating invariants

Loading does not start playback. Typed loading protects playing decks and verifies the exact path. `sync --deck 2 --to 1` changes deck 2 to match deck 1's playback BPM within 0.05 BPM; it does not request beat/phrase alignment.

Transition and skip return submission, while typed state-changing commands verify their stated effects. Inspect state after a timeout and never automatically resubmit mutations. Status is sequential.

Paired stems from one recording share a timeline at their original speed even when independent BPM analysis disagrees. Prefer no-sync transitions and absolute file-position checks for those stems.

## Development

Use the specification in `docs/specs/2026-10-12-cli-bridge.md` and evidence in `docs/research/cli-validation.md`. Use `main` as the default and integration branch. Use `codex/` names only for feature branches, then integrate completed work into `main`. Preserve important milestones in Git. Keep credentials, personal machine paths, native SDK headers, source audio and private backups out of Git.

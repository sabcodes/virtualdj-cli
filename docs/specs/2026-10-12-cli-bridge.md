# VirtualDJ CLI — milestone 1

Status: implementation authorized by the user after discussing the CLI/plugin approach; local files first explicitly selected. Live VirtualDJ Free compatibility remains a release gate.

## Goal and accepted constraints

Agents run CLI commands to control the already-open VirtualDJ app through its documented plugin SDK, VDJScript and Automix. No mouse, keyboard, screen capture, accessibility automation, replacement DJ engine, paid Network Control/OSC dependency, or streaming-service integration.

Platform: existing Apple Silicon macOS installation. A basic SDK plugin uses a user/session-local Core Foundation message port. It dispatches scripts and queries on the main run loop. The CLI uses Python standard library and ctypes; no daemon or dependency packages.

## Command contract

- `vdj doctor`: bridge connection, app build/version and license query; unavailable bridge is an actionable nonzero JSON error.
- `vdj status [--deck 1|2]`: track path/title/artist/key, BPM, elapsed/remaining milliseconds, playing state, crossfader and Automix. Snapshot is a sequence of queries, not atomic.
- `vdj load --deck 1|2 PATH [--replace-playing]`: absolute local path; protect playing decks by default and confirm the loaded path. Loading does not start playback.
- `vdj play|pause --deck 1|2`: idempotent transport actions followed by state verification.
- `vdj transition --beats N [--no-sync]`: invoke documented mix_now or mix_now_nosync. Reject when Automix is active (its own transition settings govern duration). Report command acceptance, not completion or guaranteed musical quality.
- `vdj automix start|stop|next|status`: explicit enable/disable/skip/query. Playlist selection remains in VirtualDJ for this milestone.
- `vdj query SCRIPT [--type number|text]` and `vdj script SCRIPT`: explicit advanced access to the SDK's documented query/execute callbacks. Raw scripts can change any state exposed by VDJScript.
- All output is JSON; exit 0 success, 1 operational error, 2 invalid arguments. No automatic mutation retries.

## Runtime boundaries

Local message port is named per user in the macOS bootstrap session, not exposed over TCP. Requests are bounded, UTF-8 and carry a deadline. Expired requests are rejected before dispatch; a timeout during execution means an unknown outcome, so inspect state before trying again. Callbacks never process audio. Startup does not send playback commands. SDK success means accepted submission; only query-confirmed actions report verified state. Reject control characters, quotes and backticks in typed load paths rather than invent undocumented VDJScript escaping.

## Acceptance and evidence

1. Native arm64 bundle compiles against checksum-pinned official SDK headers; SDK remains ignored and is fetched locally, not redistributed.
2. The real message-port/CLI pipeline runs against fake SDK callbacks: transport, UTF-8 output, argument rejection, guarded load, mutation verification, failed SDK calls, deadline rejection and unavailable bridge.
3. Install only our new bundle in the discovered user AutoStart directory. Do not modify app binaries, licenses, existing plugins or settings. User opens/reopens VirtualDJ manually to load it.
4. Live gate: doctor identifies the real app and Free license; status queries work; local load confirms path; Automix and transition behavior is exercised with user-approved test audio. Until then, label the project as a feasibility prototype, not verified Free support.
5. Agent usage instructions explain JSON and outcome verification; no skills are installed globally until this live gate passes.

## Sources

- https://virtualdj.com/wiki/Developers.html
- https://virtualdj.com/wiki/Plugins_SDKv8.html
- https://virtualdj.com/manuals/virtualdj/appendix/vdjscriptverbs.html
- https://virtualdj.com/manuals/virtualdj/interface/browser/sideview/automix.html
- https://virtualdj.com/wiki/NetworkControlPlugin (official HTTP requires Pro)
- https://virtualdj.com/manuals/virtualdj/appendix/optionslist.html (OSC requires Pro)

## Milestones

M1: spec, build, CLI, native IPC harness, new plugin installed, commit/push; live gate explicitly recorded.
M2: validate Free-edition runtime and agent workflow, then persist/install the skill.
M3: explicit BPM sync and a reusable agent skill for local-file workflows.

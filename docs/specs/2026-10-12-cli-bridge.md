# VirtualDJ CLI — milestone 1

Status: local-file milestone implemented and live-verified on the user-reported Free installation; reusable agent skill installed.

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
3. Install only our new bundle in the documented user SoundEffect directory; manually select the basic plugin once per app session. Do not modify app binaries, licenses, existing plugins or settings. User opens/reopens VirtualDJ manually to load it.
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

Loader revision: the AutoStart attempt did not expose the bridge on the user's Free installation. The SDK basic-plugin documentation/forum directs basic plugins to SoundEffect. AutoStart has historically required Pro. Testing the supported manual effects route next; this does not establish compatibility until live queries succeed.

## Milestone evidence update

Live selection on the user-reported Free build 9644 verified native communication, state queries, exact local loading, transport and a four-beat no-sync transition with silent audio. Eight regression tests pass. License introspection is unavailable and is reported as unknown. Musical quality, phrase alignment, live Automix start/next are still outside verified coverage; the user’s existing two-track Automix queue was preserved. Install the agent skill with those explicit limits.

## BPM sync addition — 2026-10-12

User request: add an agent tool to sync BPM. Contract: `vdj sync --deck TARGET --to SOURCE`, with explicit, distinct decks 1 or 2. Read the source's current playback BPM once, then submit the documented `deck TARGET pitch BPM bpm` exactly once. This changes playback tempo rather than analyzed BPM metadata; it does not request playback, beat/phrase alignment or a master-deck change.

Require both decks loaded, positive finite BPM on both decks, Automix stopped, and target Pitch Lock off (do not change the user's lock setting). Verify the target matches the captured BPM within 0.05 BPM and the source still matches that value. Return target/source deck, before BPM, observed BPM and reference BPM with `verified: true` only after verification. A changed reference, SDK rejection, no-op or pitch-range clamp can fail verification; never retry the mutation automatically. Settings and track analysis can change between sequential queries.

Acceptance: native harness covers both directions, source/transport preservation, invalid/unloaded decks, invalid BPM, Automix/Pitch Lock rejection and nonfatal no-op acknowledgement with a single submission. Verify against the running app, capture the result, update agent usage instructions and push the milestone. Paired stems of one recording retain a common timeline at their original speed; their independent BPM estimates need not agree.

BPM sync acceptance evidence: twelve harness tests pass; live target BPM matched within 0.002 BPM on build 9644 with source tempo, absolute file positions and transport preserved. Original target pitch restored after testing. Ordinary elapsed time is tempo-scaled and cannot establish an unchanged file position.

## Reusable agent skill — 2026-10-12

After confirming the setup works, the user requested reusable skill instructions. Update the existing virtualdj-cli skill in the repo and installed skills directory, keeping their executable-location guidance appropriate to each location. Include connection/state checks, outcome verification, explicit target/source BPM sync, paired-stem timing, Automix prerequisites and recovery without mutation retries. Documentation-only acceptance: validate both skills and check examples against CLI help; do not trigger playback for skill packaging. Preserve automatic discovery.

## Project scope and publication - 2026-10-12

Project name: VirtualDJ CLI. Repository: https://github.com/sabcodes/virtualdj-cli. Support local filesystem music only; account and streaming-service integrations are outside this tool. Public history uses the GitHub username/noreply identity and generic paths. Private recovery backups stay outside the public repository.

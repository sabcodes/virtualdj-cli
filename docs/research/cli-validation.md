# CLI bridge validation — 2026-10-12

## Verified locally

- Native arm64 bundle compiled against official SDK archive SHA-256 `77c23717509838f518d3176b088b97e8242ce357c2d78ce851d70386ae9f341e`.
- Ad-hoc code signature verified for installed bundle; exported SDK entry point is `DllGetClassObject`.
- Six native-IPC integration tests pass against fake SDK callbacks. They exercise actual Core Foundation messaging and the CLI as subprocesses, not a mocked transport.
- Tests cover UTF-8/JSON output, guarded local-file loading, transport and Automix state verification, transition submission, SDK rejection/nonfinite results, invalid arguments/injection characters, missing bridge and expired mutation rejection.
- Obsidian CLI created and read back `Projects/VirtualDJ CLI/Context.md` in the user's configured Obsidian vault.

## Runtime gate remains open

The user manually opened VirtualDJ. Real `doctor` and `status` returned `bridge_unavailable` after the first AutoStart installation. The signed basic plugin was moved to the SDK-documented SoundEffect location. The user is being guided to select it in the master effect dropdown; no successful real SDK callback has yet been observed.

Native tests do not establish Free license compatibility, native app plugin discovery/activation, real audio loading, audio quality or transition timing. No real-app playback commands have been sent. Startup logs contain only plugin lifecycle markers, not songs, credentials or script text.

The agent skill exists as a repo-local draft. The bundled quick validator could not run because PyYAML is absent from both available Python runtimes. Required name/description frontmatter and operational instructions were reviewed manually; the skill is not installed globally while live validation is incomplete.

## Next check

User selects Agent CLI Bridge beside the vertical MASTER label in Performance layout. Query the app through `./vdj doctor` and `./vdj status`; inspect our startup-only log if unavailable. A directory move or repeated unavailable query must not be treated as success.

## Live validation completed after manual plugin selection

- The plugin is visible in the master effects list as AgentCLIBridge. Manual selection exposes the native message port; no desktop automation was used.
- Actual build is now 9644, version 2026. User states Free; the SDK `get_license` text query returns S_FALSE, so automated entitlement identification remains unavailable.
- `get_version` must be formatted through `get_text` for this SDK callback. Empty decks must be queried with `loaded` before metadata; absent fields are not evidence of a failed connection.
- Real SendCommand can return positive S_FALSE even when it applies a command. Updated handling treats that as nonfatal submission while typed commands independently verify their effects. Negative SDK errors still fail. Regression coverage ensures a no-effect submission cannot be reported as a verified load.
- Both generated 30-second silent WAVs loaded successfully and returned exact paths, BPM, elapsed/remaining times, title and artist. Play/pause states were verified.
- A four-beat no-sync transition started deck 2 and moved the crossfader through approximately 0.04, 0.20, 0.36, 0.53, 0.70, 0.86 to 1.0. This verifies command execution/crossfade progression, not audio quality or phrase matching.
- Test tracks were unloaded, playback stopped and original crossfader 0.5 restored. The existing Automix queue had two tracks and was kept intact; only Automix status/stop were tested live. Start/next remain harness-tested.
- Eight native integration tests pass. Corrected 0.1.1 bundle compiles and is installed with an identified backup; the current live session used the original 0.1.0 plugin with compatible CLI handling. The new bundle loads on the next manual app restart.

## Real stem playback test — 2026-10-12

User requested audible testing with existing Stem Splitter output. Used the matching drums.wav and vocals.wav from Orion Sun — Mirage, an existing local Stem Splitter output directory. Both files are stereo PCM16 at 44.1 kHz and approximately 57.5 seconds. No source audio was modified or committed.

Verified exact loads, simultaneous start at zero, both playing flags, matching elapsed positions, positive master meter activity and an eight-beat no-sync crossfade from 0 to 1. Samples progressed from 51,391 ms to 55,701 ms equally on both decks; master meter values varied approximately 0.003–1.0. Returned crossfader to 0.5 to blend stems. No claim about physical speaker output or subjective musical quality; evidence is app playback state and signal meter.

The real files exposed a readiness race: loaded can become true before get_filepath produces a value. Previously that transient S_FALSE aborted verification even though loading later succeeded. The CLI now waits through that specific nonfatal query result until its existing deadline, without resubmitting the load mutation; negative SDK and transport errors still fail. A native integration test reproduced the failure first, then verified successful loading with exactly one load submission. Nine tests pass. Both real files subsequently returned verified:true through typed load commands with a five-second deadline.

These stems produced differing independently analyzed BPM/key values despite matching playback positions. For paired stems from one recording, preserve their shared timeline and use no-sync instead of stretching one to match the other’s estimator.

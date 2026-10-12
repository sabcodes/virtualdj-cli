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

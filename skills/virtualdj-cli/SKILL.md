---
name: virtualdj-cli
description: Control running VirtualDJ on macOS through its CLI bridge. Use for local-song or stem loading, playback, BPM sync, transitions, Automix and deck-state checks.
---

# VirtualDJ CLI

Operate VirtualDJ through the installed native bridge and CLI. The user opens the app and selects **Agent CLI Bridge** (shown as **AgentCLIBridge**) from the master effects dropdown once per app session. Agents use terminal commands; the workflow does not use desktop input automation.

Last live verification: VirtualDJ 2026 build 9644, user-reported Free. Local loading, transport, BPM sync and no-sync crossfades worked; the user subsequently confirmed the setup works. Automix start/next have native harness coverage, while status/stop are also live-tested. Track loading is limited to local audio files.

## Locate the CLI

In the repository, resolve `../../vdj` relative to this skill directory. If the skill is copied elsewhere, use the user-configured `VDJ_CLI_BIN` or locate the intended executable on PATH.

Set `VDJ_CLI_BIN` to that resolved absolute executable path and quote it in every shell call because the checkout name contains spaces. Use `"$VDJ_CLI_BIN" --help` or a subcommand's `--help` to inspect current arguments. Typed commands currently address decks **1 and 2**, even if the app displays four decks.

## Operate and verify

1. Run `doctor`, then `status`. Continue when the bridge is connected and the intended deck/track is identified. Status is sequential, not an atomic snapshot.
2. Choose the action from the user's request. For loading, resolve the intended local file and choose a stopped deck; loading alone does not start playback. Use `--replace-playing` only when replacing that playing track is intended.
3. Run the typed command and inspect its JSON. Exit 0 is success, 1 is an operational failure, and 2 is invalid arguments. Load, transport, sync and Automix on/off report `verified: true` after querying their effects.
4. For transitions, skips or raw scripts, `submitted: true` means submission only. Query status afterwards and report the observed result; a callback or playing flag alone does not establish audible output or musical quality.

Example: when the user asks to load, match and play a second local song following deck 1, inspect deck 1 as the reference and deck 2 as the target, then:

```bash
"$VDJ_CLI_BIN" doctor
"$VDJ_CLI_BIN" status
"$VDJ_CLI_BIN" load --deck 2 '/absolute/path/to/song.wav'
"$VDJ_CLI_BIN" sync --deck 2 --to 1
"$VDJ_CLI_BIN" play --deck 2
"$VDJ_CLI_BIN" status
```

Execute each command only after checking the preceding result. For slow-opening files, `--timeout 5` goes **before** the subcommand; load verification polls metadata readiness without repeating the load.

## BPM sync

`sync --deck 2 --to 1` changes **deck 2** to follow **deck 1**. Reverse the numbers to change deck 1. Both decks must be loaded with positive BPM, Automix stopped and target Pitch Lock off. If those settings conflict with the user's intent, report the conflict instead of silently disabling them.

This matches playback tempo through an explicit BPM action; it does not edit the analyzed beatgrid, start playback or request beat/phrase alignment. Success confirms the target within **0.05 BPM** of the captured source and checks that the source still agrees. Source analysis or settings may change between queries.

For separate stems of the **same recording**, preserve their common starting position and original speed unless tempo changes are requested. Independent stem BPM estimates can disagree despite a shared timeline. Prefer `transition --beats 8 --no-sync` for those stems. Compare absolute file positions with `query 'deck 2 get_position'` or `query 'deck 2 get_time "elapsed" "absolute"'`; ordinary elapsed time rescales with pitch.

## Other commands

| Action | Command arguments after the executable |
| --- | --- |
| Inspect one deck | `status --deck 1` |
| Pause | `pause --deck 1` |
| Transition using engine sync | `transition --beats 8` |
| Transition preserving tempos | `transition --beats 8 --no-sync` |
| Automix | `automix start`, `stop`, `next` or `status` |
| Numeric query | `query 'deck 1 get_bpm'` |
| Text query | `query 'deck 1 get_filepath' --type text` |
| Advanced action | `script 'VDJScript'` |

Transition requires both decks loaded and Automix stopped. Playlist selection/queuing remains inside VirtualDJ; Automix start needs a nonempty queue, and next needs active Automix. Raw scripts bypass typed guards: use them for understood actions within the requested scope and query their effects. Consult the [official verb reference](https://virtualdj.com/manuals/virtualdj/appendix/vdjscriptverbs.html) when an advanced action requires it.

## Failures and reporting

- **Bridge unavailable:** ask the user to open/reopen VirtualDJ and select the master-effect plugin. Resume once they report it ready; repeated unavailable calls do not establish a connection.
- **Mutation timeout or SDK rejection:** inspect state before deciding what to do. Never automatically repeat a load, sync, skip or transition; its outcome may be unknown.
- **Sandbox blocks native IPC:** use the normal execution-permission flow and report the actual error.
- **Missing metadata/license:** empty decks and absent tags can return null fields; an unavailable license query means unknown entitlement. A positive SDK execution result can still be a no-op, so rely on queried verification.
- **Playback report:** distinguish loaded file, playing state, signal level and the user's listening confirmation. A master meter may come from the other deck.

Finish with the chosen file/deck, any BPM change and the verified or submitted outcome. Accept local filesystem paths for track loading.

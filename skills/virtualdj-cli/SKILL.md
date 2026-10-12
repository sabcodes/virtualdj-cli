---
name: virtualdj-cli
description: Operate a running VirtualDJ instance through the local macOS CLI bridge for deck state, local-track loading, playback, Automix and transitions. Use when the user wants agents to control VirtualDJ from terminal commands.
---

# VirtualDJ CLI

Availability: feasibility prototype. Native IPC is tested against simulated SDK callbacks; real Free-edition compatibility must be established. Run `doctor` against the real app before performing mutations. A successful test-harness response is not evidence about VirtualDJ.

## Locate and connect

In this repository the executable is `../../vdj` relative to this skill directory. If the skill has been copied elsewhere, locate `vdj` on PATH or use the user-configured `VDJ_CLI_BIN`; do not assume another checkout's path. Use the executable's absolute path for shell calls.

The user opens VirtualDJ and selects **Agent CLI Bridge** in the master effects dropdown. Agents operate exclusively through the CLI; they do not take desktop focus, send keystrokes, click controls, alter licensing.

Run `vdj doctor`, then `vdj status`. If `bridge_unavailable` occurs, ask the user to open/reopen the app and select the plugin; do not retry the same unavailable connection repeatedly or switch to GUI automation. Sandbox restrictions may independently block native local IPC; report the actual error and use the normal authorized execution-permission flow.

## Commands

```bash
vdj doctor
vdj status --deck 1
vdj load --deck 2 '/absolute/path/to/song.wav'
vdj play --deck 2
vdj pause --deck 1
vdj transition --beats 8
vdj transition --beats 8 --no-sync
vdj automix start
vdj automix next
vdj automix stop
vdj automix status
vdj query 'deck 1 get_bpm'
vdj query 'deck 1 get_filepath' --type text
```

Output is JSON. Exit 0 means the command's stated result succeeded; 1 means an operational failure; 2 means invalid arguments. `--help` describes current arguments.

- Loading alone does not authorize starting playback. Typed load protects playing decks and verifies the loaded path. Use `--replace-playing` only when the user intends to replace that playing track.
- Playlist selection/queuing is performed inside VirtualDJ in this milestone. Automix start requires a nonempty queue; next requires active Automix. Stop Automix before requesting a custom transition duration.
- Transition returns `submitted`, not a completed or musically verified transition. Inspect deck state afterwards. Beat matching is conditional on VirtualDJ's engine and track tempos; it does not guarantee phrase alignment.
- Status consists of sequential queries, not an atomic snapshot. Use it to choose the appropriate deck and avoid overwriting the live track.
- SDK rejection, transport timeout or verification timeout is a real failure/unknown outcome. Inspect state before retrying a mutation; never automatically repeat a load, skip or transition.
- Prefer typed commands. Advanced `vdj script 'VDJScript'` submits raw scripts without typed guards. Use it only for an understood action within the user's requested scope, and verify its effect with queries. See the [official verb reference](https://virtualdj.com/manuals/virtualdj/appendix/vdjscriptverbs.html).


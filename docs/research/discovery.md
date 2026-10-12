# VirtualDJ CLI - discovery

Date: 2026-10-12
Repository: https://github.com/sabcodes/virtualdj-cli

Goal: let agents operate the already-open VirtualDJ app through terminal commands for local music files. Reuse the app's playback, VDJScript and Automix engine.

Platform: Apple Silicon macOS. The user reports the Free edition. Native runtime support must be verified before reporting an operation as working.

Boundaries: local filesystem tracks; no desktop input automation, replacement DJ engine or streaming-service integration. Use specification-driven development and preserve important milestones in Git.

Primary references:
- https://virtualdj.com/wiki/Developers.html
- https://virtualdj.com/wiki/Plugins_SDKv8.html
- https://virtualdj.com/manuals/virtualdj/appendix/vdjscriptverbs.html

Initial research is followed by the [bridge specification](../specs/2026-10-12-cli-bridge.md) and [validation evidence](cli-validation.md).

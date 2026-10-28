# Claude Code adapter

Use the shared [contracts](contracts.md) and [role prompts](roles.md). Claude Code discovers the root `skills/` tree through `.claude-plugin/plugin.json`.

Direct invocation is `/pstack-quant:quant-research`, with focused skills available under the same plugin namespace. No hooks or bootstrap agents run at session start. Normal domain-appropriate skill selection remains available.

Read the active `CLAUDE.md` and existing pstack model configuration. Resolve the configured role names against Claude Code's available native models. Codex model slugs are not Claude Code model names. Do not modify the user's settings. Preserve the existing configured independent panel, including repeated entries as separate agents.

Use the native `Agent` tool for each specialist when it is available. Set the configured model and effort according to its current tool schema. Give the agent absolute shared role/reference paths, the source evidence and hash, one private output directory, a bounded deliverable, and stopping conditions. Use `Read`, `Grep`, `Glob`, `Write`, `Edit`, and `Bash` only when actually exposed by the session. These are host capabilities, not dependencies supplied by this plugin.

A native assignment can use a general-purpose agent with a prompt that reads `<plugin-root>/skills/quant-research/references/roles.md` and selects the assigned role. No custom agent type is required. `${CLAUDE_PLUGIN_ROOT}` is available in plugin command contexts where documented by Claude Code. In loaded skill prose, resolve the root from the skill's installed file location instead of assuming shell variable expansion.

When `Agent` is unavailable, keep required review seats blocked and continue nongated work. A single session performing multiple perspectives is not independent review. Report missing capabilities in the run's decision receipt and final report.

The [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference) defines manifest and component paths. The [marketplace reference](https://code.claude.com/docs/en/plugin-marketplaces) defines local relative plugin sources. Local native Claude execution was unavailable during development. The CI manifest-validation job uses the official CLI and does not establish research execution or model behavior.

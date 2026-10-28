# Codex adapter

Use the shared [contracts](contracts.md) and [role prompts](roles.md). The adapter supplies host mechanics only.

## Discover and invoke

Install through the repository marketplace described in the [README](../../../README.md). Invoke `$quant-research` or a focused `$quant-*` skill directly, or allow normal domain-appropriate skill selection. `agents/openai.yaml` keeps implicit invocation enabled. No session hook changes unrelated work.

Read the active `AGENTS.md` and existing Codex pstack model configuration, normally `~/.codex/pstack-models.md`. Session instructions override defaults. Do not modify configuration as part of a research task. Preserve configured effort; `session` omits an effort override.

Use tools actually present in the session. The common capability mapping is:

| Action | Codex capability |
| --- | --- |
| Read and search | Shell command tool with `cat`, `rg`, and `rg --files` |
| Edit local outputs | `apply_patch` or the available file tool |
| Run evidence or user research command | Shell execution tool, with the plugin script's absolute path |
| Dispatch independent specialist | `spawn_agent`, sometimes exposed as `collaboration.spawn_agent` |
| Receive and wait | The host's corresponding agent message and wait tools |
| Save checkpoints | Exclusive files under the run directory |

Discover tool signatures before calling. Some hosts use different argument names or do not expose multi-agent tools. When dispatch is unavailable, preserve missing required seats as blocked. Do not invent a generic `Agent` tool on Codex or silently reduce an independent panel.

## Model roles and independent seats

Map hypothesis and design to `judgment and prose`, implementation to `feature, refactoring`, and specialist investigation to the configured explorer or investigator role. Independent scientific reviewers use `interrogate reviewers`, reproduction uses `swarm workers`, and priority review uses the host's priority extension. A configured `auto` or `inherit-parent` omits a model override.

For the user configuration this plugin was built against, code and judgment use `gpt-6.1-sol`. The independent reviewer panel is exactly:

```text
seat 1: gpt-6.1-sol, fresh session
seat 2: gpt-6.1-sol, fresh session
seat 3: gpt-6-luna, fresh session
```

The repeated Sol row is two independent agents. If the runtime accepts the configured `gpt-6.1-luna` preference, use it for the Luna role. Otherwise use configured fallback `gpt-6-luna`. A capacity rejection is not a model rejection. Keep the remaining seats blocked until capacity is available. Do not substitute a different model for Sol. Use a new stage-specific panel when preregistration and result review both require panels.

The minimal evidence schema requires a preregistration methodology seat and methodology, execution-risk, and reproduction result seats. Expand `review_seats` before registration to retain the configured panel for each required review stage. Give every seat a separate ID and unique reviewer session. A methodology panel does not replace the execution-risk or reproduction roles.

In a runtime exposing this session's collaboration schema, one dispatch looks like:

```text
collaboration.spawn_agent(
  task_name="pre-method-1",
  fork_turns="none",
  model="gpt-6.1-sol",
  message="Read <plugin-root>/skills/quant-research/references/roles.md. Role: methodology preregistration reviewer. Seat: pre-method-1. Inspect RUN/trials/t001/plan.json and registration.json. Registration sha256: <hash>. Authors to exclude: <IDs>. Write only RUN/work/<unique-session>/. Produce review.json using references/evidence.md. Budget: <limit>. Do not run the experiment or access holdout."
)
```

Use absolute installed plugin paths in real assignments. Pass source paths and hashes instead of long copied transcripts. When capacity requires sequential agents, preserve separate sessions and review artifacts. The coordinator verifies and publishes receipts; reviewers never write the same dossier path.

## Existing-session campaigns

Route long runs and repeated multi-study missions to [quant-campaign](../../quant-campaign/SKILL.md). The campaign coordinator owns the cumulative ledger and bounded commitments; preserve configured independent seats and private worker outputs. Discover actual native continuation and honor its authorization policy. Durable state supports compaction and manual or native resume but does not schedule wakeups or guarantee host uptime. Do not launch replacement sessions or install hooks.

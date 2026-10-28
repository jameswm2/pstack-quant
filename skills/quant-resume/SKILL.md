---
name: quant-resume
description: Resume a quantitative research run by verifying saved artifacts, trial accounting, and priority state.
---

# Quant resume

For long autonomous runs, competing mechanisms, or repeated study programs, use [quant-campaign](../quant-campaign/SKILL.md). If the root contains `charter/spec.json`, run `tools/campaign.py view ROOT` and follow the campaign contract before reusing evidence or assigning work. For a campaign, return its actual-root `continuation_prompt`, `next_command`, and `next_action`, including exact head, original mission and deadline, and pending assignment. Reconcile before dispatch and do not replay completed units. Individual studies keep their original inspection and scientific gates.

Read the shared [research contracts](../quant-research/references/contracts.md), then the [role prompts](../quant-research/references/roles.md) for this phase. Use the current host adapter linked from [quant-research](../quant-research/SKILL.md). These references own gates and independence; this entry point only narrows the assignment.

Run inspect before trusting prior work. Read the latest ordered decision receipt and compare counters with the priority triggers. Preserve failed and old results, name missing independent reviewers, and select one bounded next assignment. Never reset the family budget by creating a new run.

Read the [methodology](../quant-research/references/methodology.md) for research judgments and [evidence schema](../quant-research/references/evidence.md) for artifacts. Resolve the plugin root as `../..` from this skill file. Write only in the user-authorized research workspace.

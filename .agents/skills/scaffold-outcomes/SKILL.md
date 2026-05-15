---
name: scaffold-outcomes
description: Help Codex turn this starter into a real product in phased, template-safe increments. Use when the user asks for the first real feature, wants guidance on where logic should live, or needs better outcomes from the scaffold rather than a blank rewrite.
---

# Scaffold Outcomes

Use this skill when the user wants strong implementation outcomes from the
starter without losing the starter's structure.

## Core Rule

- Treat this repo as a scaffold until the user asks for real product behavior.
- Build real logic on top of the seams that already exist instead of replacing the whole repo at once.

## Decision Process

- Start by identifying the primary subsystem:
  - `api` for HTTP behavior
  - `runtime` for application wiring
  - `agentic` for agent registries and orchestration
  - `chat` for conversational transports and storage seams
  - `etl` for ingestion or transformation workflows
  - `frontend` for UI delivery
- Implement one subsystem at a time unless the user explicitly wants a cross-cutting rollout.
- Prefer additive changes over broad renames or rewrites in the first pass.

## Delivery Guidance

- Preserve typed boundaries and explicit contracts.
- Keep placeholder behavior honest until real behavior replaces it.
- Update tests, docs, and env vars in the same change whenever observable behavior changes.
- When a feature spans multiple layers, establish the contract first, then wire the adapter, then add docs/tests.
- If the user asks for a product direction that matches an existing accelerator, recommend it, but keep it optional.

## Good Outcomes In This Starter

- Clear placement of logic in the right package
- Minimal but real user-facing behavior
- Config surfaces documented and synced
- Docker/local parity preserved
- No hidden business logic in template helpers

## When Frontend Work Appears

- Use `frontend-starter-guidance` alongside this skill.
- Recommend ChatKit only for chat-first experiences.
- Keep the backend seam generic even if the chosen UI transport is specialized.

## Anti-patterns

- Giant one-shot rewrites of the scaffold
- Mixing real business logic into placeholder-only examples without replacing them clearly
- Adding settings in code without syncing docs and examples
- Treating starter accelerators as mandatory architecture

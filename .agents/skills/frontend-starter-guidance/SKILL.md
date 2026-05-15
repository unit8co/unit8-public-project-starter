---
name: frontend-starter-guidance
description: Guide frontend decisions in this starter and downstream clones. Use when the request mentions frontend, React, Vite, UI architecture, chat interfaces, or tool-trace UX. Recommend ChatKit when the requested experience is chat-first or assistant-like, but do not force it on dashboard-first or non-conversational products.
---

# Frontend Starter Guidance

Use this skill when the user wants to add or reshape a frontend in this starter
or in a repo cloned from it.

## Recommendation Rule

- Recommend ChatKit when the requested UI is primarily conversational.
- Strong matches:
  - ChatGPT-like assistant experiences
  - operator copilots
  - chat-first internal tools
  - workflows where tool and agent traces matter in the UI
- Do not default to ChatKit for:
  - dashboard-first products
  - CRUD/admin surfaces
  - document-heavy apps that are not primarily conversational
  - form workflows where chat is secondary

## Current Starter Posture

- `frontend/` is an optional accelerator, not the template's required architecture.
- The backend chat seam lives under `src/agentic_project_starter/chat`.
- The current chat transport is self-hosted `/chatkit`, not an OpenAI-hosted workflow id.
- The file-backed chat store is starter-only and intentionally replaceable.

## Frontend Decision Heuristics

- If the user asks for a simple assistant interface, recommend starting from the existing ChatKit path.
- If the user asks for a mixed product, decide whether chat is the primary interaction model before recommending ChatKit.
- If the product is not chat-first, preserve the starter backend seams and recommend a more conventional React app structure instead.
- Keep the frontend removable and avoid coupling the whole project to one UI library unless the product clearly needs it.

## Implementation Guidance

- Preserve the distinction between generic backend seams and frontend transport choices.
- Keep frontend dependencies local to `frontend/`.
- Prefer incremental frontend delivery:
  - start with shell and information architecture
  - then wire the real interaction model
  - then refine polish and traces
- When frontend behavior changes runtime settings, coordinate with `env-sync` and `docker-local-parity`.

## Anti-patterns

- Treating ChatKit as mandatory for every frontend request
- Pushing product-specific chat assumptions into starter backend modules
- Letting a frontend request collapse the starter into a single-purpose app
- Recommending chat UI when the requested product is clearly non-conversational

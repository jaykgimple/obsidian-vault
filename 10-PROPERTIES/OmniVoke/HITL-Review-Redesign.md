# HITL Review Redesign (collapsed summary + expandable rows + asset slot)

**Date:** 2026-09-26
**Property:** OmniVoke
**Status:** builder dispatched (deleg_d6214877), critic pending

## Why

The HITL review surface (`src/components/Review.tsx`, 1063 lines) rendered one near-identical card per platform, each with the same Edit/Save/Publish/Reject controls. 9 platforms = 9 copies of the same mess. Jay's ask: "I still want HITL, i just dont want a mess of things to review. need to consider assets for all the platforms not just youtube." His own suggestion was expandable cards.

## Design bar (acceptance test)

1. **Collapsed summary first.** One compact row per platform: label + status chip (Ready/Rendering/Needs review/Rejected/Published) + one-line preview. No edit controls collapsed. All platforms scannable at once.
2. **Expandable rows.** Expand inline → full editor whose centerpiece is the platform's ACTUAL asset: video for YouTube, image for INSTAGRAM/PINTEREST/BLUESKY/FACEBOOK, text for LINKEDIN/TWITTER/MASTODON/REDDIT. Keeps existing capabilities (edit text, edit script, Save, Publish-one, Reject-modal, YouTube segment-regenerate flow, two-phase video script→render→preview→publish).
3. **Single global action.** One "Approve & publish all" enabled only when every non-rejected platform is ready; rejected rows excluded, never blocking.
4. **Asset-slot abstraction.** PlatformAsset kind (video|image|text|pending) so image/text platforms stop being second-class. Seam Jay explicitly wants.

## Constraints

- No API route signature changes; keep pending.ts public shape.
- WCAG 2.2 AA standing bar.
- No new npm deps; pure-logic tests only if no jsdom/react-testing lib present.
- No em dashes in user-facing copy.

## Known pre-existing test failures (out of scope for this piece)

- generateHashtags / generateCalendar / dispatchGenerate "without a key" (3)
- buildRenderPlan avatar warning (1)

## Source truth

- Component: src/components/Review.tsx
- Persisted queue: src/lib/review/pending.ts
- Publish: src/lib/publish/* (registry + 9 adapters)
- Media: prisma MediaAsset { kind: video|thumbnail, key (R2) }
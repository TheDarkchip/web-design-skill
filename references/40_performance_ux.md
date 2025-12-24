# Performance as UX (perceived speed + stability)

Performance issues often feel like “bad design”:
- Layout shift breaks trust and causes misclicks.
- Slow interaction makes UI feel unresponsive.
- Delayed content causes users to abandon.

## Practical checks
- Reserve space for images/embeds to prevent layout shift.
- Avoid inserting banners above content after load.
- Prefer skeletons for large content regions.
- Defer non-critical scripts; avoid blocking rendering.

## UX-friendly loading
- Show progress for long actions.
- Don’t disable the entire UI unnecessarily; disable only what must be blocked.
- Provide optimistic UI cautiously and rollback safely.

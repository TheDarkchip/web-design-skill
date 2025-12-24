# WCAG-aligned quick checks (practical, not legal advice)

This is a **field checklist** for common web UI issues.

## Keyboard
- All interactive elements reachable via Tab.
- Logical tab order.
- **Visible focus** (not removed).
- No keyboard traps (Escape closes dialogs).

## Semantics
- Use semantic elements: button for actions, a for navigation.
- One main landmark (`<main>`), page has `<h1>`.
- Headings are nested logically (avoid skipping levels).

## Names & labels
- Inputs have labels (explicit `<label for>` or implicit wrap).
- Buttons/links have discernible text or `aria-label`.
- Icons alone must have accessible names.

## Forms
- Required fields identified (and announced).
- Errors are specific, near the field, and programmatically associated.
- Don’t rely on color alone to convey errors.

## Images & media
- Informative images have meaningful `alt`.
- Decorative images use empty `alt=""`.
- Video has captions; audio has transcripts (when applicable).

## Motion and contrast
- Don’t convey meaning only by color.
- Support reduced motion (`prefers-reduced-motion`) for non-essential animation.
- Ensure readable contrast for text and UI states (treat as mandatory even if you can’t compute it here).

## Zoom & responsive
- Works at 200% zoom without losing content or requiring horizontal scroll (common goal).
- Touch targets are large enough and spaced (especially on mobile).

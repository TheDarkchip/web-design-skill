# Design principles (the coach’s vocabulary)

Use these terms in explanations. Prefer one principle per fix.

## Clarity
Users should understand **what this is**, **what to do**, and **what happens next** in ~2–5 seconds.
- Make the primary action visually dominant.
- Reduce competing emphasis (too many “primary” buttons).
- Prefer familiar patterns over novelty.

## Feedback
Every action should produce timely, perceivable feedback.
- Loading states, pressed states, inline validation.
- Prevent double-submit and ambiguous success.

## Consistency
Similar things should look and behave similarly.
- Same component = same padding, typography, states.
- One spacing scale, one radius scale, one icon style.

## Accessibility
Everything must be usable with keyboard, screen readers, zoom, and reduced motion.
- Semantic HTML first.
- Visible focus.
- Text alternatives and labels.

## Error prevention & recovery
Prevent errors; when they happen, help users recover fast.
- Validate early, but politely.
- Errors near the field; explain how to fix.
- Preserve input; avoid wiping forms.

## Efficiency
Make frequent tasks fast without hiding discoverability.
- Defaults, sensible autofill, progressive disclosure.
- Reduce steps, not control.

## Trust
Users judge credibility from clarity + stability.
- Avoid layout shift.
- Avoid surprise navigation.
- Use reassuring microcopy and predictable states.

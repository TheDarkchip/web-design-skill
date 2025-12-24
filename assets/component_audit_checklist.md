# Component audit checklist

Use this when reviewing any reusable component.

## Anatomy
- [ ] Clear purpose and usage examples
- [ ] Variants are explicit (size, tone, state)

## States
- [ ] Default / Hover / Active / Focus / Disabled
- [ ] Loading (if async)
- [ ] Error/success (if form-related)

## Accessibility
- [ ] Semantic element used (button/link/input)
- [ ] Keyboard operable; visible focus
- [ ] Accessible name (label/aria-label)
- [ ] ARIA only when needed; no broken roles

## Layout
- [ ] Consistent padding/spacing tokens
- [ ] Aligns cleanly in common layouts
- [ ] Doesn’t overflow on small screens

## Content
- [ ] Text is concise; avoids ambiguity
- [ ] Supports localization (no fixed widths that break)

## Performance
- [ ] Doesn’t cause layout shift
- [ ] Avoids heavy JS for simple behavior

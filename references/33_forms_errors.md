# Forms, validation, and error handling

## Form layout
- Prefer one column for most forms (especially on mobile).
- Group related fields; keep labels close to inputs.
- Use inline hints only when necessary; keep them short.

## Validation strategy
- Validate constraints that block submission (format, required) early but gently.
- On submit, focus the first invalid field and summarize errors at the top if many.
- Preserve user input on errors.

## Error messages
- Plain language, specific, and actionable.
- Put error text near the field and associate it programmatically.
- Don’t shame users; avoid “invalid” without explanation.

## Defaults and input types
- Use correct input types (`email`, `tel`, `number` cautiously).
- Prefer dropdowns only when options are limited and stable.
- Provide examples for ambiguous formats (date, phone).

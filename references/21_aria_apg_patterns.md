# ARIA & interactive patterns (APG-inspired)

Rule of thumb: **Use semantic HTML first**. Use ARIA only when you’re building custom widgets.

## Modal dialog
- Use a semantic dialog (`<dialog>`) if feasible or correct ARIA for custom.
- Focus moves into the dialog on open; returns to trigger on close.
- Escape closes; background content not focusable while open.
- The dialog has a clear title and close affordance.

## Menus / dropdowns
- Don’t use “menu” ARIA for simple nav lists; use normal links.
- For complex widgets (combobox, listbox), follow established keyboard patterns.

## Tabs
- Use tablist/tabpanel semantics if custom.
- Arrow keys move between tabs; Tab moves into panel.

## Tooltips
- Tooltips are not for essential info.
- Don’t hijack focus; tooltip should appear on hover/focus and disappear predictably.

## Toasts / alerts
- Important errors should be `role="alert"` (sparingly).
- Don’t spam announcements; make them meaningful.

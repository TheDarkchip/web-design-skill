# Scripts

These scripts are optional helpers the skill can run for deterministic checks.

## ui_audit.py
A lightweight, dependency-free HTML audit that flags common issues:
- missing lang/title/viewport
- missing <main>
- missing labels on form fields
- empty links/buttons
- missing image alt attributes
- duplicate IDs
- heading level jumps

Examples:
- `python scripts/ui_audit.py assets/sample_bad.html --format md`
- `python scripts/ui_audit.py assets/sample_bad.html --format json`

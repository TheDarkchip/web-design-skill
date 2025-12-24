#!/usr/bin/env python3
"""graspable-web-design-coach/scripts/ui_audit.py

A lightweight, dependency-free HTML audit script to catch common UX/a11y footguns.

This is intentionally conservative: it flags probable issues and provides remediation hints.
It does NOT claim WCAG compliance.

Usage:
  python scripts/ui_audit.py path/to/file.html --format md
  python scripts/ui_audit.py path/to/file.html --format json

Exit codes:
  0: ran successfully (even if issues were found)
  2: file read/parse error
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Issue:
    severity: str          # "high" | "med" | "low"
    category: str          # "accessibility" | "semantics" | "forms" | "content" | "structure" | "responsive" | "interaction"
    message: str
    hint: str
    line: Optional[int] = None
    col: Optional[int] = None
    element: Optional[str] = None


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: List[Tuple[str, Dict[str, str], int, int]] = []  # tag, attrs, line, col

        # Document-level facts
        self.has_html = False
        self.html_lang: Optional[str] = None
        self.has_title = False
        self.title_text: str = ""
        self.has_meta_viewport = False
        self.has_main = False

        # IDs / labels
        self.ids: Dict[str, Tuple[int, int]] = {}
        self.duplicate_ids: List[Tuple[str, int, int]] = []
        self.labels_for: Dict[str, Tuple[int, int]] = {}  # id -> location of label[for]

        # Headings
        self.heading_levels: List[Tuple[int, int, int]] = []  # level, line, col

        # Anchors and buttons: capture discernible text
        self.current_link: Optional[Dict[str, Any]] = None
        self.links: List[Dict[str, Any]] = []
        self.current_button: Optional[Dict[str, Any]] = None
        self.buttons: List[Dict[str, Any]] = []

        # Inputs
        self.inputs: List[Dict[str, Any]] = []

        # Images
        self.images: List[Dict[str, Any]] = []

        # Skip link detection
        self.skip_link_candidates: List[Dict[str, Any]] = []

    def _pos(self) -> Tuple[int, int]:
        return self.getpos()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        line, col = self._pos()
        a = {k.lower(): (v if v is not None else "") for k, v in attrs}

        # Track stack for implicit label detection
        self.stack.append((tag.lower(), a, line, col))

        if tag.lower() == "html":
            self.has_html = True
            self.html_lang = a.get("lang") or None

        if tag.lower() == "meta":
            if (a.get("name") or "").lower() == "viewport":
                self.has_meta_viewport = True

        if tag.lower() == "main":
            self.has_main = True

        # IDs + duplicates
        if "id" in a and a["id"].strip():
            _id = a["id"].strip()
            if _id in self.ids:
                self.duplicate_ids.append((_id, line, col))
            else:
                self.ids[_id] = (line, col)

        # <label for="...">
        if tag.lower() == "label":
            f = (a.get("for") or "").strip()
            if f:
                self.labels_for[f] = (line, col)

        # Headings
        if tag.lower() in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            lvl = int(tag[1])
            self.heading_levels.append((lvl, line, col))

        # Images
        if tag.lower() == "img":
            self.images.append({
                "attrs": a,
                "line": line,
                "col": col
            })

        # Links
        if tag.lower() == "a":
            self.current_link = {
                "attrs": a,
                "text": "",
                "line": line,
                "col": col
            }

        # Buttons
        if tag.lower() == "button":
            self.current_button = {
                "attrs": a,
                "text": "",
                "line": line,
                "col": col,
                "in_form": any(t == "form" for t, *_ in self.stack[:-1]),
            }

        # Inputs
        if tag.lower() in {"input", "select", "textarea"}:
            implicit_label = any(t == "label" for t, *_ in self.stack[:-1])
            self.inputs.append({
                "tag": tag.lower(),
                "attrs": a,
                "line": line,
                "col": col,
                "implicit_label": implicit_label,
                "in_form": any(t == "form" for t, *_ in self.stack[:-1]),
            })

    def handle_endtag(self, tag: str):
        tag = tag.lower()

        # Close link
        if tag == "a" and self.current_link is not None:
            self.links.append(self.current_link)
            self.current_link = None

        # Close button
        if tag == "button" and self.current_button is not None:
            self.buttons.append(self.current_button)
            self.current_button = None

        # Pop stack until tag found (best effort, handles malformed HTML)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data: str):
        text = (data or "").strip()
        if not text:
            return

        if self.stack and self.stack[-1][0] == "title":
            self.has_title = True
            self.title_text += text

        if self.current_link is not None:
            self.current_link["text"] += " " + text

        if self.current_button is not None:
            self.current_button["text"] += " " + text


def _discernible_text(text: str) -> str:
    return " ".join((text or "").split()).strip()


def audit(html: str) -> List[Issue]:
    p = AuditParser()
    try:
        p.feed(html)
        p.close()
    except Exception as e:
        return [Issue(
            severity="high",
            category="structure",
            message=f"Failed to parse HTML: {e}",
            hint="Check for malformed markup; try validating the HTML.",
        )]

    issues: List[Issue] = []

    # Document basics
    if not p.has_html:
        issues.append(Issue(
            severity="med",
            category="structure",
            message="Missing <html> root element.",
            hint="Ensure the document has a proper <!doctype html> and <html> root.",
        ))
    else:
        if not p.html_lang:
            issues.append(Issue(
                severity="high",
                category="accessibility",
                message="Missing lang attribute on <html>.",
                hint='Add a language, e.g. <html lang="en">, to improve screen reader behavior.',
                element="html",
            ))

    if not p.has_title or not p.title_text.strip():
        issues.append(Issue(
            severity="med",
            category="content",
            message="Missing or empty <title>.",
            hint="Add a descriptive page title (helps tabs and assistive tech).",
            element="title",
        ))

    if not p.has_meta_viewport:
        issues.append(Issue(
            severity="high",
            category="responsive",
            message='Missing <meta name="viewport"> (mobile rendering may be broken).',
            hint='Add: <meta name="viewport" content="width=device-width, initial-scale=1">',
            element="meta[name=viewport]",
        ))

    if not p.has_main:
        issues.append(Issue(
            severity="med",
            category="semantics",
            message="No <main> landmark found.",
            hint="Wrap primary page content in <main> to improve navigation for assistive tech.",
            element="main",
        ))

    # Duplicate IDs
    for _id, line, col in p.duplicate_ids:
        issues.append(Issue(
            severity="high",
            category="semantics",
            message=f'Duplicate id "{_id}" detected.',
            hint="IDs must be unique. Rename one of the elements or remove the duplicate id.",
            line=line,
            col=col,
            element=f'#{_id}',
        ))

    # Headings: presence and order
    h1_count = sum(1 for lvl, *_ in p.heading_levels if lvl == 1)
    if h1_count == 0:
        issues.append(Issue(
            severity="med",
            category="structure",
            message="No <h1> found.",
            hint="Add a single <h1> that describes the page/section for clear hierarchy.",
            element="h1",
        ))
    elif h1_count > 1:
        issues.append(Issue(
            severity="low",
            category="structure",
            message=f"Multiple <h1> elements found ({h1_count}).",
            hint="Often best to keep one primary <h1>. If multiple are used, ensure it’s intentional and structured.",
            element="h1",
        ))

    # Heading level jumps
    last = None
    for lvl, line, col in p.heading_levels:
        if last is not None and lvl - last > 1:
            issues.append(Issue(
                severity="low",
                category="structure",
                message=f"Heading level jumps from h{last} to h{lvl}.",
                hint="Avoid skipping heading levels; it can confuse outline navigation for assistive tech.",
                line=line,
                col=col,
                element=f"h{lvl}",
            ))
        last = lvl

    # Images: alt
    for img in p.images:
        a = img["attrs"]
        alt_present = "alt" in a
        alt_text = (a.get("alt") or "").strip()
        if not alt_present:
            issues.append(Issue(
                severity="high",
                category="accessibility",
                message="Image missing alt attribute.",
                hint='Add alt text. Use alt="" for decorative images; meaningful text for informative images.',
                line=img["line"],
                col=img["col"],
                element="img",
            ))
        elif alt_text == "":
            # Empty alt can be correct; keep low
            issues.append(Issue(
                severity="low",
                category="accessibility",
                message='Image has empty alt="". Ensure this image is purely decorative.',
                hint='If the image conveys meaning, provide descriptive alt text. If decorative, alt="" is correct.',
                line=img["line"],
                col=img["col"],
                element="img",
            ))

    # Links: href and discernible text
    skip_detected = False
    for link in p.links:
        a = link["attrs"]
        text = _discernible_text(link["text"])
        href = (a.get("href") or "").strip()
        aria = (a.get("aria-label") or "").strip()

        if not href:
            issues.append(Issue(
                severity="med",
                category="interaction",
                message="Anchor <a> without href found.",
                hint='Use <button> for actions, or add a valid href for navigation links.',
                line=link["line"],
                col=link["col"],
                element="a",
            ))

        if not text and not aria:
            issues.append(Issue(
                severity="high",
                category="accessibility",
                message="Link has no discernible text (empty link).",
                hint="Add visible link text or aria-label. If it’s an icon link, aria-label is required.",
                line=link["line"],
                col=link["col"],
                element="a",
            ))

        if href.startswith("#") and ("skip" in text.lower() or "skip" in aria.lower()):
            skip_detected = True

    if not skip_detected:
        issues.append(Issue(
            severity="low",
            category="accessibility",
            message="No obvious 'Skip to content' link detected.",
            hint="Consider adding a visually-hidden skip link for keyboard users (especially on content-heavy pages).",
            element="a[href^=#]",
        ))

    # Buttons: discernible text, type in forms
    for btn in p.buttons:
        a = btn["attrs"]
        text = _discernible_text(btn["text"])
        aria = (a.get("aria-label") or "").strip()
        if not text and not aria:
            issues.append(Issue(
                severity="high",
                category="accessibility",
                message="Button has no discernible text (empty button).",
                hint="Add button text or aria-label. Icon-only buttons require aria-label.",
                line=btn["line"],
                col=btn["col"],
                element="button",
            ))
        if btn["in_form"] and "type" not in a:
            issues.append(Issue(
                severity="low",
                category="forms",
                message="Button inside form missing type attribute (defaults to submit).",
                hint='Add type="button" for non-submit buttons to avoid accidental form submits.',
                line=btn["line"],
                col=btn["col"],
                element="button",
            ))

    # Inputs: labels
    for inp in p.inputs:
        a = inp["attrs"]
        _id = (a.get("id") or "").strip()
        aria_label = (a.get("aria-label") or "").strip()
        aria_labelledby = (a.get("aria-labelledby") or "").strip()
        has_explicit_label = bool(_id and _id in p.labels_for)
        has_implicit_label = bool(inp["implicit_label"])
        placeholder = (a.get("placeholder") or "").strip()

        if not (has_explicit_label or has_implicit_label or aria_label or aria_labelledby):
            issues.append(Issue(
                severity="high",
                category="accessibility",
                message=f"{inp['tag']} appears to be missing an associated label.",
                hint="Add a <label> (preferred) or aria-label/aria-labelledby. Placeholder is not a label.",
                line=inp["line"],
                col=inp["col"],
                element=inp["tag"],
            ))
        elif placeholder and not (has_explicit_label or has_implicit_label) and not (aria_label or aria_labelledby):
            issues.append(Issue(
                severity="med",
                category="forms",
                message=f"{inp['tag']} uses placeholder text but no real label.",
                hint="Add a visible label; placeholders disappear on input and reduce accessibility.",
                line=inp["line"],
                col=inp["col"],
                element=inp["tag"],
            ))

    return issues


def issues_to_markdown(issues: List[Issue]) -> str:
    if not issues:
        return "## UI Audit\n\nNo issues detected by the lightweight audit (this is not a full accessibility review).\n"

    order = {"high": 0, "med": 1, "low": 2}
    issues_sorted = sorted(issues, key=lambda x: (order.get(x.severity, 9), x.category, x.message))

    lines: List[str] = []
    lines.append("## UI Audit (lightweight, dependency-free)\n")
    lines.append("> Note: This script flags common issues. It does **not** guarantee WCAG compliance.\n")

    for sev in ["high", "med", "low"]:
        bucket = [i for i in issues_sorted if i.severity == sev]
        if not bucket:
            continue
        title = {"high": "High", "med": "Medium", "low": "Low"}[sev]
        lines.append(f"### {title} priority\n")
        for i in bucket:
            loc = ""
            if i.line is not None:
                loc = f" (line {i.line}:{i.col or 0})"
            elem = f"`{i.element}` " if i.element else ""
            lines.append(f"- {elem}**{i.message}**{loc}\n  - Hint: {i.hint}\n")
        lines.append("")
    return "\n".join(lines)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Lightweight HTML UI/a11y audit (no dependencies).")
    ap.add_argument("html_file", help="Path to an HTML file to audit.")
    ap.add_argument("--format", choices=["md", "json"], default="md", help="Output format.")
    args = ap.parse_args(argv)

    path = Path(args.html_file)
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        return 2

    issues = audit(html)

    if args.format == "json":
        print(json.dumps([asdict(i) for i in issues], indent=2))
    else:
        print(issues_to_markdown(issues))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

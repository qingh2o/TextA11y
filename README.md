# web-text-a11y-audit: Automated Text Accessibility Auditor

web-text-a11y-audit is an automated web accessibility auditing tool developed as a capstone project for UX/UI and software engineering evaluations. Built using **Python**, **Selenium WebDriver**, and **SQLite**, the engine acts as an automated web scraper and compliance evaluator. It dynamically maps, extracts, and validates on-screen textual components against official W3C Web Content Accessibility Guidelines (WCAG) 2.2 Relative Luminance Contrast Standards.

The software architecture is heavily inspired by Dr. Chuck’s (Dr. Charles Severance) data design patterns: implementing an asynchronous pipeline that handles extraction, data cleanup, relational normalization, and foreign-key mapping inside a relational database system.

---

## 🚀 Key Features & Architectural Highlights

* **Universal Semantic Extraction:** Utilizes an advanced universal XPath parser to scrape text strings inside the HTML `<body>` while completely ignoring non-visual nodes (`<script>`, `<style>`, `<noscript>`, `<template>`, and `<svg>`).
* **Anonymous Text Node Extraction:** Features an injected custom JavaScript execution bridge (`nodeType === 3`) capable of isolating and preserving raw text strings separated by layout break tags (`<br>`), solving a major structural data-loss flaw common in basic web scrapers.
* **Robust DOM Tree Climbing:** Climbs structural parent layouts dynamically if a text node inherits transparency (`rgba(0,0,0,0)`), accurately tracking down the real rendered background color layout container.
* **Alphanumeric Context Filters:** Integrates an advanced regular expression processing engine to eliminate visual design artifacts (such as decorative pipelines `|  |`, borders, or empty wrappers) from skewing compliance metrics.
* **Pre-Seeded Relational Data:** Implements a strict relational SQLite schema mapping automated findings with consistent foreign key indices for data integrity.
* **Interactive Terminal Control:** Dynamic execution allows engineers to provide target testing URLs and custom database filenames natively on initialization.

---

## 🔍 "Pixel Sampling Validator Required" Triggers

A core strength of the web-text-a11y-audit engine is its defensive handling of complex UI rendering environments. Standard relative luminance formulas can only evaluate flat, solid hex/RGB color properties. When encountering complex CSS backgrounds, the application bypasses standard math evaluations to avoid false data and flags the element with a **"Pixel sampling validator Required"** warning. 

This condition is automatically triggered if the engine catches any of the following during tree-climbing evaluation:
1. **Background Images:** The parent container features a `background-image` property containing a `url(...)` string.
2. **CSS Gradients:** The background style resolves to a `linear-gradient` or `radial-gradient` rule string.
3. **Semi-Transparency:** The resolved `background-color` contains an alpha channel lower than 1.0 (`alpha < 1.0`), indicating a translucent color layer blending with underlying layout content.

These entries are preserved in the ledger to indicate that an eye-dropper pixel sampling or manual design inspection is necessary to verify WCAG compliance.

---

## 🛠️ Tech Stack & Dependencies

* **Language:** Python 3.14.6
* **Automation Engine:** Selenium WebDriver (Chromium Engine)
* **Database Engine:** SQLite 3
* **Compliance Protocol:** W3C WCAG 2.2 Success Criteria 1.4.3 (Contrast Minimum)

---
## 📂 Project Architecture

```text
WEBA11Y/
│
├── audit.py          # Core runner file containing automation and pipeline loops
├── utils.py          # Math utilities, WCAG luminance ratios, and typeface weights
├── .gitignore        # System configuration to exclude runtime binaries and databases
└── README.md         # Documentation file






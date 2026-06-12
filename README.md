# web-text-a11y-audit: Automated Text Accessibility Auditor

**web-text-a11y-audit** is an automated web text accessibility auditing tool developed specifically for UX/UI designers, testers, and developers to evaluate web page text accessibility. Built using **Python**, **Selenium WebDriver**, and **SQLite**, the engine acts as an automated web scraper and compliance evaluator. It dynamically maps, extracts, and validates on-screen textual components against official W3C Web Content Accessibility Guidelines (WCAG) 2.2 Relative Luminance Contrast Standards.

The software architecture is heavily inspired by Dr. Chuck’s (Dr. Charles Severance) data design patterns: implementing an asynchronous pipeline that handles extraction, data cleanup, relational normalization, and foreign-key mapping inside a relational database system.

---

## 🚀 Key Features & Architectural Highlights

* **Dynamic Viewport Scrolling** (Lazy-Load Bypass): Integrates a sequential programmatic scrolling routine to trigger Intersection Observers and CSS fade-in animations (like inview classes), ensuring hidden or lazy-loaded text elements are fully rendered and captured by the DOM scraper before evaluation.
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

* **Language:** Python 3.12+
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

```
---

## 📊 Database Schema Details

The application creates two normalized data entities inside the generated SQLite binary file:

### 1. Status (Lookup Entity)

Stores clean categorical outcomes ensuring highly optimized indexing performance:
* **id** (INTEGER, Primary Key)
* **status** (TEXT: PASS, FAIL, or Pixel sampling validator Required)

### 2. Texta11y (Core Audit Ledger)

Tracks individual DOM typographic configurations evaluated:
* **id** (INTEGER, Primary Key)
* **tag** (TEXT) - Original HTML element descriptor
* **text_content** (TEXT) - Extracted textual content
* **text_color** (TEXT) - Extracted color profile string
* **bg_color** (TEXT) - Computed container background color string
* **contrast_ratio** (REAL) - Calculated relative contrast math ratio (Returns NULL if complex layout requires pixel validation)
* **font_size** (INTEGER) - Computed size converted to integer pixel units
* **font_weight** (INTEGER) - Standardized typographic thickness weight
* **level_aa_id**(INTEGER) - Foreign Key pointing to the definitive Status record

---

## ⚙️ Installation & Local Setup

1. Clone the Repository

2. Install Required Python Dependencies
Ensure you have the required browser orchestration framework configured:

```

pip install selenium

```
> **Note:** 
> WebDriver management for Google Chrome is handled natively by contemporary versions of Selenium, but ensure you have Google Chrome installed.

3. Install DB Browser for SQLite
The audit results are stored in a **SQLite database file** (.sqlite). To inspect, query, and export the generated audit data. After the audit completes, open the generated .sqlite file using **DB Browser** for SQLite to review the audit records.

4. Execute the auditor module from your terminal:

```

py audit.py

```

## 🖥️ Prompt Configurations:

Upon launching, the engine will prompt you for configuration details:

1. **Database name**: Type a name for your data file (e.g., data11y). The application automatically structures and appends .sqlite layout extensions if omitted.
2. **Target URL**: Paste any live web system page URL to launch scanning operations. (Pressing Enter without input defaults the runner to a pre-set test link).


## 🎯 Terminal Reporting Output Sample:

```
=======================================================
UX/UI Text Accessibility Audit Engine
=======================================================
Enter database name: texta11y
Enter the audit target URL: https://example.com

🚀 Initializing database: texta11y.sqlite
🌐 Target URL: https://example.com

Scanning elements ...
Note: Browser will close automatically when finished!
-------------------------------------------------------
WCAG 2.2 AA Level Audit Summary Report
-------------------------------------------------------
📊 Total Text Elements Audited: 178
❌ Total Text Elements Failed: 12
⚠️ Total Pixel Sampling Required: 17
✅ Total Text Elements Passing : 149
=======================================================
Audit Completed - Database Refreshed
=======================================================
💡 Tip:
1. Open 'texta11y.sqlite' in 'DB Browser for SQLite'
2. Inspect the detailed 'Texta11y' and 'Status' tables.

```

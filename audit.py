from selenium import webdriver
from selenium.webdriver.common.by import By 
from utils import *
import time
import re
import sqlite3

# ----------------------------------------------------------------------
# Step 0: User Configuration Inputs
# ----------------------------------------------------------------------
print("="*55)
print("UX/UI Text Accessibility Audit Engine")
print("="*55)

# 1. Database File Prompt (Appends .sqlite automatically if omitted)
db_input = input("Enter database name: ").strip()
if not db_input:
    db_input = "texta11y"  # Default backup name if left blank

if not db_input.endswith(".sqlite"):
    db_filename = db_input + ".sqlite"
else:
    db_filename = db_input

# 2. URL Prompt (With a quick-test default)
target_url = input("Enter the audit target URL: ").strip()
if not target_url:
    target_url = "https://norvigaward.github.io/entries.html"

print(f"\n🚀 Initializing database: '{db_filename}'")
print(f"🌐 Target URL: {target_url}")

# ----------------------------------------------------------------------
# Step 1.  Database Initialization
# ----------------------------------------------------------------------
conn = sqlite3.connect(db_filename)
cur = conn.cursor()

# ----create 2 tables
cur.executescript('''
DROP TABLE IF EXISTS Status;
DROP TABLE IF EXISTS Texta11y;

CREATE TABLE Status (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    status TEXT UNIQUE
);

CREATE TABLE Texta11y (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    tag TEXT,
    text_content TEXT,
    text_color TEXT,
    bg_color TEXT,
    contrast_ratio REAL,
    font_size  INTEGER,
    font_weight  INTEGER,
    level_aa_id  INTEGER,
    FOREIGN KEY(level_aa_id) REFERENCES Status(id)
);
''')

# Hard-seed the statuses so IDs are fixed, predictable, and clean
# ID 1 = PASS, ID 2 = FAIL, ID 3 = Pixel sampling validator Required
statuses = ["PASS", "FAIL", "Pixel sampling validator Required"]
for s in statuses:
    cur.execute('INSERT OR IGNORE INTO Status (status) VALUES (?)', (s,))
conn.commit()

# ----------------------------------------------------------------------
# Step 2: Browser Automation Start and Engine loop
# ----------------------------------------------------------------------
driver = webdriver.Chrome()
driver.set_window_size(1200, 550)
driver.get(target_url)

# FIX: Scroll down the page sequentially to trigger 'inview' elements
scroll_height = driver.execute_script("return document.body.scrollHeight")
for i in range(0, scroll_height, 600):
    driver.execute_script(f"window.scrollTo(0, {i});")
    time.sleep(0.3) # Give CSS animations time to switch opacity to 1

time.sleep(1) # Final buffer for the page to settle


# Finds any element on the page containing raw, visible text strings
text_elements = driver.find_elements(
    By.XPATH, 
    "//body//*[normalize-space(text()) != '' and not(self::script) and not(self::style) and not(self::noscript) and not(self::template) and not(self::svg)]"
)

print("\nScanning elements ... \nNote: Browser will close automatically when finished")

for element in text_elements:
    # FILTER 1: Skip elements that are visually hidden on the screen
    if not element.is_displayed():
        continue
    tag_name = element.tag_name

# ADVANCED JAVASCRIPT EXTRACTOR:
    # Gathers all direct text fragments (nodeType 3) belonging to THIS element, 
    # joining them if they are split by <br> tags, while ignoring sub-element tags.
    text_content = driver.execute_script("""
        var parent = arguments[0];
        var textResult = "";
        for (var i = 0; i < parent.childNodes.length; i++) {
            var node = parent.childNodes[i];
            if (node.nodeType === 3) { // 3 means it's a raw text node
                textResult += node.nodeValue;
            }
        }
        return textResult;
    """, element)
    
    if text_content is None:
        text_content = ""   
    text_content = text_content.replace('\n', '').replace('\r', '').strip()

    # FILTER 2: Skip empty strings or whitespace noise
    if not text_content:
        continue 

    # FILTER 3: Skip isolated UI micro-characters (like the '×' close icon)
    # These are structural design symbols, not actual paragraph prose
    if text_content in ["×", "X", "*", "•", "»", "«"]:
        continue 

    # NEW FILTER 4: Clean out purely decorative structural symbols (like "|  |", "---", or "/")
    # This pattern checks if the text contains ONLY punctuation, symbols, and whitespace.
    # If there are NO letters or numbers at all, it skips it!
    if not re.search(r'[a-zA-Z0-9]', text_content):
        continue

# Ask Selenium for the computed CSS color properties
    text_color = element.value_of_css_property("color")
    bg_color = element.value_of_css_property("background-color")
    current_bg = bg_color
    current_element = element

# Loop upwards ONLY while the background is completely transparent
    while current_bg == "rgba(0, 0, 0, 0)" or current_bg == "transparent":
        try:
            parent_element = current_element.find_element(By.XPATH, "..")
            current_bg = parent_element.value_of_css_property("background-color")
            current_element = parent_element 
        except:
            break

# Also fetch background-image properties of the final container to look for images/gradients
    bg_image = current_element.value_of_css_property("background-image")

# Font Processing
    font_size_px = element.value_of_css_property("font-size")
    font_size = int(float(font_size_px.replace("px", "").strip()))

# Standardize font weight to an integer
    font_weight_raw = element.value_of_css_property("font-weight").strip().lower()

    if font_weight_raw.isdigit():
        font_weight = int(font_weight_raw)
    elif font_weight_raw in weight_map:
        font_weight = weight_map[font_weight_raw]
    else:
        font_weight = 400

# --------------------------Audit Filters
# 1. Extract alpha value of the background found
    alpha = get_alpha(current_bg)

# 2. Check if background contains an image or linear-gradient string
    has_image_or_gradient = "url(" in bg_image or "gradient" in bg_image

# 3. Apply your customized audit filtering rule
    if current_bg == "rgba(0, 0, 0, 0)" or alpha < 1.0 or has_image_or_gradient:
        final_ratio = None
        aa_status = "Pixel sampling validator Required"

    else:
        # Compute real WCAG math ratio
        final_ratio = round(calculate_contrast(text_color, current_bg), 1)

        # Determine if text is Large Text vs Normal Text
        if font_size >= 24 or (font_size >= 18.5 and font_weight >= 700):
            if final_ratio >= 3.0:
                aa_status = "PASS"
            else:
                aa_status = "FAIL"
        else:
            if final_ratio >= 4.5:
                aa_status = "PASS"
            else:
                aa_status = "FAIL"

# 4. Database Synchronization
    cur.execute('INSERT OR IGNORE INTO Status (status) VALUES ( ? )', ( aa_status, ) )
    cur.execute('SELECT id FROM Status WHERE status = ? ', (aa_status, ))
    level_aa_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Texta11y 
                (tag, text_content, text_color, bg_color, contrast_ratio, font_size, font_weight, level_aa_id ) 
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )''', 
                ( tag_name, text_content, text_color, current_bg, final_ratio, font_size, font_weight, level_aa_id ) )


# Query 1: Total Failures
cur.execute('''
    SELECT COUNT(*) FROM Texta11y 
    JOIN Status ON Texta11y.level_aa_id = Status.id 
    WHERE Status.status = 'FAIL'
''')
total_failures = cur.fetchone()[0]

# Query 2: Total Pixel Sampling Validator Required
cur.execute('''
    SELECT COUNT(*) FROM Texta11y 
    JOIN Status ON Texta11y.level_aa_id = Status.id 
    WHERE Status.status = 'Pixel sampling validator Required'
''')
total_sampling = cur.fetchone()[0]

# Query 3: Total Passes (Optional but good for context!)
cur.execute('''
    SELECT COUNT(*) FROM Texta11y 
    JOIN Status ON Texta11y.level_aa_id = Status.id 
    WHERE Status.status = 'PASS'
''')
total_passes = cur.fetchone()[0]

print("-"*55)
print("WCAG 2.2 AA Level Audit Summary Report")
print("-"*55)

print(f"📊 Total Text Elements Audited: {total_failures + total_sampling + total_passes}")
print(f"❌ Total Text Elements Failed: {total_failures}")
print(f"⚠️ Total Pixel Sampling Required: {total_sampling}")
print(f"✅ Total Text Elements Passing: {total_passes}")


# ----------------------------------------------------------------------
# Step 3: Clean wrap-up
# ----------------------------------------------------------------------
conn.commit()
driver.quit()
cur.close()
conn.close()

print("="*55)
print("Audit Completed - Database Refreshed")
print("="*55)
print(f"💡 Tip: \n1. Open '{db_filename}' in 'DB Browser for SQLite' \n2. Inspect the detailed 'Texta11y' and 'Status' tables.\n")
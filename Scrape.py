from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import random
import re

# ---------- CONFIG ----------
EMAIL = [EMAIL] 
PASSWORD = [PASSWORD]
PROFILE_URLS = [
    "https://www.linkedin.com/in/supun-prabodha-liyanage/",
    "https://www.linkedin.com/in/satyanadella/",
    "https://www.linkedin.com/in/mattgarman/",
]
CSV_FILE = "linkedin_profiles.csv"
# ----------------------------

def setup_driver():
    """Set up Chrome WebDriver with options."""
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    # opts.add_argument("--headless=new")  # Uncomment for headless mode
    return webdriver.Chrome(options=opts)

def check_captcha(driver):
    """Check for CAPTCHA/puzzle and wait for manual resolution."""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".checkpoint-container")) or
            EC.presence_of_element_located((By.ID, "captcha")) or  # Generic CAPTCHA ID
            EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))  # reCAPTCHA
        )
        print("⚠️ Puzzle/CAPTCHA detected. Please solve it manually in the browser.")
        WebDriverWait(driver, 300).until_not(  # Wait up to 5 minutes for resolution
            EC.presence_of_element_located((By.CSS_SELECTOR, ".checkpoint-container")) or
            EC.presence_of_element_located((By.ID, "captcha")) or
            EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
        )
        print("✔ Puzzle/CAPTCHA resolved.")
    except:
        pass  # No CAPTCHA

def login(driver, email, password):
    """Log in to LinkedIn and handle post-login puzzle/page change."""
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(email)
    pw = driver.find_element(By.ID, "password")
    pw.send_keys(password)
    pw.send_keys(Keys.RETURN)
    time.sleep(2)  # Initial delay to allow login attempt
    check_captcha(driver)  # Check for CAPTCHA/puzzle after login attempt
    
    # Wait for a stable post-login page (e.g., homepage or profile-accessible state)
    WebDriverWait(driver, 60).until(
        lambda d: any(keyword in d.current_url for keyword in ["feed", "home", "profile"])
        or d.find_elements(By.CSS_SELECTOR, ".global-nav")  # Check for nav bar (indicating logged-in state)
    )
    time.sleep(3)  # Additional delay to ensure page stabilizes after CAPTCHA

def scrape_profile(driver, url):
    """Scrape name, headline, location, and URL from a LinkedIn profile."""
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    # Multiple scrolls to ensure content loads
    for _ in range(2):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)

    # Name
    name = ""
    try:
        name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "main h1"))
        ).text.strip()
    except:
        name = "Name not found"

    # Headline
    headline = ""
    for sel in [
        ".text-body-medium",
        ".pv-text-details__left-panel .text-body-medium",
        ".pv-top-card--list li.text-body-small",
    ]:
        try:
            txt = driver.find_element(By.CSS_SELECTOR, sel).text.strip()
            if txt:
                headline = txt
                break
        except:
            pass
    if not headline:
        title = (driver.title or "").replace(" | LinkedIn", "")
        if " - " in title:
            parts = title.split(" - ", 1)
            if len(parts) == 2:
                headline = parts[1].strip()
    headline = headline or "Headline not found"

    # Location (broadened selectors)
    location = ""
    for sel in [
        ".pv-text-details__left-panel .text-body-small",  # Primary
        ".pv-top-card--list-bullet li.text-body-small",   # Newer layout
        ".pb2.t-black--light.t-14",                       # Public profile
        ".t-14.t-black--light",                           # Broader fallback
        "div.pv-top-card--list-bullet span",              # Generic top card
    ]:
        try:
            txt = driver.find_element(By.CSS_SELECTOR, sel).text.strip()
            if txt and ("," in txt or txt in ["United States", "Canada"]):  # Location-like text
                location = txt
                break
        except:
            pass

    # Debug: Print all text in profile header for inspection
    if not location:
        print(f"⚠️ Debug: Location not found for {url}. Dumping visible text for inspection...")
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, ".pv-top-card, .pv-text-details__left-panel, .pv-top-card--list-bullet")
            for el in elements:
                text = el.text.strip()
                if text and len(text) < 150:  # Limit to short texts
                    print(f"  - Found text: {text}")
        except:
            print("  - No relevant text found in header.")
        
        # Fallback: Search page source for city/country pattern and clean it
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            # Look for patterns like "City, Region" or "City, Province/District"
            location_match = re.search(r'(?:[A-Za-z\s]+,\s+[A-Za-z\s]+(?:Province|District)?)', page_text)
            if location_match:
                raw_location = location_match.group(0)
                # Clean up by taking the last line that looks like a location
                location_lines = [line.strip() for line in raw_location.split('\n') if line.strip()]
                for line in reversed(location_lines):
                    if "," in line and not any(keyword in line.lower() for keyword in ["undergraduate", "sliit", "ai"]):
                        location = line
                        print(f"  - Fallback: Found location '{location}' in page text.")
                        break
                if not location:
                    location = location_lines[-1] if location_lines else "Location not found"
                    print(f"  - Fallback: Found location '{location}' in page text.")
        except:
            pass
    location = location or "Location not found"

    return {"name": name, "headline": headline, "location": location, "url": url}

def ensure_csv_header(path):
    """Write CSV header if file doesn't exist."""
    try:
        with open(path, "r", encoding="utf-8") as _:
            return  # File exists, assume header present
    except FileNotFoundError:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Name", "Headline", "Location", "Profile URL"])

def append_row(path, row):
    """Append a row to the CSV file."""
    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([row["name"], row["headline"], row["location"], row["url"]])

def main():
    """Main function to scrape profiles and save to CSV."""
    driver = setup_driver()
    try:
        login(driver, EMAIL, PASSWORD)
        ensure_csv_header(CSV_FILE)

        for url in PROFILE_URLS:
            try:
                data = scrape_profile(driver, url)
                append_row(CSV_FILE, data)
                print(f"✅ Saved: {data['name']} | {data['headline']} | {data['location']}")
                time.sleep(random.uniform(2, 5))  # Longer random delay
            except Exception as e:
                print(f"⚠️ Failed for {url}: {e}")
    finally:
        driver.quit()
        print(f"\nAll done. Check {CSV_FILE}")

if __name__ == "__main__":
    main()
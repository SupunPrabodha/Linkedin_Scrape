# LinkedIn Profile Scraper (Selenium)

This is my **first Selenium system automation project** 🚀  
The script automates LinkedIn login, visits profile URLs, and scrapes profile details such as **Name, Headline, Location, and Profile URL**, then saves them into a CSV file.

---

## ⚙️ Features
- Automated LinkedIn login  
- CAPTCHA/manual puzzle detection support  
- Scrapes:
  - Name  
  - Headline  
  - Location  
  - Profile URL  
- Saves results into a CSV file (`linkedin_profiles.csv`)  

---

## 🖥️ Tech Stack
- **Python 3.x**  
- **Selenium WebDriver**  
- **Google Chrome + ChromeDriver**  

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/SupunPrabodha/linkedin-selenium-scraper.git
   cd linkedin-selenium-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install selenium
   ```

3. **Download & match ChromeDriver**  
   - Find your Chrome version: `chrome://settings/help`  
   - Download the matching driver from: https://chromedriver.chromium.org/downloads  
   - Place it in your system PATH.

4. **Add your LinkedIn credentials**  
   - Open the Python file and replace:
     ```python
     EMAIL = "your_email_here"
     PASSWORD = "your_password_here"
     ```
   - ⚠️ Do **not** push your real email/password to GitHub.  
     Instead, you can use environment variables or a `.env` file (recommended).

5. **Run the project**
   ```bash
   python linkedin_scraper.py
   ```

6. **Output**  
   - The scraped results will be saved into `linkedin_profiles.csv`.

---

## 📌 Notes
- If LinkedIn shows a CAPTCHA or puzzle, the script will pause until you solve it manually.  
- This project is for **educational purposes only**. Please use responsibly and respect LinkedIn’s terms of service.  

---

## 👤 Author
**Supun Prabodha**  
🔗 [GitHub: SupunPrabodha](https://github.com/SupunPrabodha)

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import random
from dotenv import load_dotenv
import os
import logging


# Load environment variables from .env
load_dotenv()


# CONFIG
INPUT_FILE = os.getenv("INPUT_FILE")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
BACKUP_FILE = os.getenv("BACKUP_FILE")
LOG_FILE = os.getenv("LOG_FILE")
COUNTRY_1 = os.getenv("COUNTRY_1")
COUNTRY_2 = os.getenv("COUNTRY_2")
SAVE_EVERY = 100
RESTART_BROWSER_EVERY = 500


# Selenium options
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(options=options)


# Create logger
def setup_logger(log_file, name="logger_details"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid re-adding handlers if already set
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


# Read input CSV
df_links = pd.read_csv(INPUT_FILE, sep='*')
df_links.columns = df_links.columns.str.strip()  # Clean column names


driver = create_driver()
wait = WebDriverWait(driver, 15)

logger = setup_logger(LOG_FILE)

results = []

# Main loop
for index, row in df_links.iterrows():

    name = row["Name"]
    url = row["Link"]
    country_1 = row.get(COUNTRY_1, "")
    country_2 = row.get(COUNTRY_2, "")
    item_index = row["Index"]

    logger.info(f"🔗 [{index+1}/{len(df_links)}] Processing: {name}")

    try:

        # Session check
        if not driver.session_id:
            logger.warning("Session lost. Create new driver...")
            driver = create_driver()
            wait = WebDriverWait(driver, 15)

        driver.get(url)
        time.sleep(random.uniform(3, 5))

        about = headquarters = website = email = phone = ""

        # About section
        try:
            # Find all matching <p> elements
            p_elements = driver.find_elements(By.CSS_SELECTOR, "p.slds-section__title.appx-section__title")

            for el in p_elements:
                html = el.get_attribute("outerHTML")
                soup = BeautifulSoup(html, "html.parser")
                p_tag = soup.find("p")

                # Get only the direct text (before nested <span>)
                direct_text = p_tag.find(string=True, recursive=False).strip()

                if direct_text.startswith("About"):
                    about = direct_text[6:].strip().replace("*", "")
                    break  # stop at first match
        except:
            pass

        # Contact sections
        items = driver.find_elements(By.CSS_SELECTOR, ".appx-extended-detail-subsection-label-description")
        for item in items:
            try:
                label = item.find_element(By.CLASS_NAME, "appx-extended-detail-subsection-label").text.strip()
                value_el = item.find_element(By.CLASS_NAME, "appx-extended-detail-subsection-description")

                if "Headquarters" in label:
                    headquarters = value_el.text.strip()
                elif "Website" in label:
                    website = value_el.find_element(By.TAG_NAME, "a").get_attribute("href")
                elif "Email" in label:
                    email = value_el.find_element(By.TAG_NAME, "a").get_attribute("href").replace("mailto:", "")
                elif "Phone" in label:
                    phone = value_el.text.strip()
            except:
                continue

        country_1_code = "".join(word[0] for word in COUNTRY_1.split())

        results.append({
            "Name": name,
            "Link": url,
            f"Country_{country_1_code}": country_1,
            f"Country_{COUNTRY_2}": country_2,
            "Index": item_index,
            "About (Short Name)": about,
            "Headquarters": headquarters,
            "Website": website,
            "Email": email,
            "Phone": phone
        })

    except Exception as e:
        logger.error(f"❌ Error for {name}: {e}")

        if "disconnected" in str(e).lower():
            logger.warning("Restoring driver after losing DevTools connection...")
            try:
                driver.quit()
            except:
                pass
            driver = create_driver()
            wait = WebDriverWait(driver, 15)

        pd.DataFrame(results).to_csv(BACKUP_FILE, index=False, encoding='utf-8-sig', sep='*')
        logger.info(f"Backup saved after error at row {index + 1}")
        continue

    # Save backup every N
    if (index + 1) % SAVE_EVERY == 0:
        pd.DataFrame(results).to_csv(BACKUP_FILE, index=False, encoding='utf-8-sig', sep='*')
        logger.info(f"Saved partial data at {index+1} entries")

    # Restart browser every M
    if (index + 1) % RESTART_BROWSER_EVERY == 0:
        logger.info("Restarting browser to clear memory...")
        driver.quit()
        driver = create_driver()
        wait = WebDriverWait(driver, 15)

    # Be polite
    time.sleep(random.uniform(0.8, 1.5))

driver.quit()

# Final save
final_df = pd.DataFrame(results)
final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig', sep='*')
logger.info(f"Done! Total saved: {len(results)} → {OUTPUT_FILE}")


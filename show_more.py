from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from dotenv import load_dotenv
import os
import logging


# Load environment variables from .env
load_dotenv()


# CONFIG
MAIN_SITE = os.getenv("MAIN_SITE")
SELECTED_COUNTRY_1 = os.getenv("COUNTRY_1")
OUTPUT_FILE_1 = os.getenv("OUTPUT_FILE_1")
LOG_FILE_1 = os.getenv("LOG_FILE_1")
SELECTED_COUNTRY_2 = os.getenv("COUNTRY_2")
OUTPUT_FILE_2 = os.getenv("OUTPUT_FILE_2")
LOG_FILE_2 = os.getenv("LOG_FILE_2")
CARD_SELECTOR = os.getenv("LISTING_CARD_SELECTOR")
APPLY_FILTER = os.getenv("APPLY_FILTER")


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')  # ensure full rendering


# Create logger
def setup_logger(log_file, name):
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


def wait_for_more_cards(driver, old_count, logger, retries=6, delay=3):
    for attempt in range(retries):
        time.sleep(delay)
        new_count = len(driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR))
        if new_count > old_count:
            return True
        logger.info(f"⏳ Waiting... ({attempt+1}/{retries}) — Still {new_count} cards")
    return False


def show_more_data(selected_country, output_file, log_file):

    driver = webdriver.Chrome(options=options)
    driver.get(MAIN_SITE)

    wait = WebDriverWait(driver, 15)

    logger = setup_logger(log_file, f"logger_{selected_country}")

    # STEP 1: Select Country
    try:
        country_dropdown = wait.until(EC.presence_of_element_located((By.ID, "select_country")))
        select = Select(country_dropdown)
        select.select_by_visible_text(selected_country)
        logger.info(f"✅ Country {selected_country} selected.")
        time.sleep(3)
    except Exception as e:
        logger.error(f"❌ Couldn't select {selected_country} from filter: {e}")
        driver.quit()
        return

    # STEP 2: Click "Apply Filters" Button
    try:
        apply_button = wait.until(EC.element_to_be_clickable((By.ID, APPLY_FILTER)))
        apply_button.click()
        logger.info("✅ 'Apply Filters' button clicked.")
        time.sleep(3)  # wait for page to reload new results
    except Exception as e:
        logger.error(f"❌ Couldn't click 'Apply Filters' button: {e}")
        driver.quit()
        return

    # Waiting until the first cards appeared
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, CARD_SELECTOR)))

    clicks = 0
    max_clicks = 75

    while clicks < max_clicks:
        try:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Count the cards before click
            before_click = len(driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR))

            # Find the button
            # show_more = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[span[text()="Show More"]]')))

            # new block
            show_more_buttons = driver.find_elements(By.XPATH, '//button[span[text()="Show More"]]')
            if not show_more_buttons:
                logger.warning("Button 'Show More' isn't available anymore , exit")
                break

            show_more = show_more_buttons[0]
            # end of the new block

            # Scroll down to find a button and make a click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", show_more)
            logger.info(f"✅ Click #{clicks+1} on 'Show more' button done successfully.")

            # Waiting for more cards
            success = wait_for_more_cards(driver, before_click, logger)
            if not success:
                logger.warning("⛔ No new cards loaded after waiting — stopping.")
                break

            clicks += 1

            # Optional pause every 30 clicks
            if clicks % 30 == 0:
                logger.info("⏸️ Pausing to reduce memory pressure...")
                time.sleep(10)

        except Exception as e:
            logger.error(f"❌ Click #{clicks+1} failed or new cards didn't appear yet: {e}")
            break

    # Collect all cards
    cards = driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR)
    logger.info(f"Total cards: {len(cards)}")

    data = []
    for card in cards:
        try:
            name = card.get_attribute('data-listing-name')
            link = card.get_attribute('href')
            data.append({"Name": name, "Link": link, "Country": selected_country})
        except Exception as e:
            logger.warning(f"⚠️ Problem with a card:  {e}")
            continue

    driver.quit()

    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig', sep='*')
        logger.info(f"✅ Data saved in the file {output_file}")
    else:
        logger.warning("⚠️ No data collected, skipping file save.")


# Run script for each country sequentially
show_more_data(SELECTED_COUNTRY_1, OUTPUT_FILE_1, LOG_FILE_1)

# Run script for each country sequentially
# show_more_data(SELECTED_COUNTRY_2, OUTPUT_FILE_2, LOG_FILE_2)
